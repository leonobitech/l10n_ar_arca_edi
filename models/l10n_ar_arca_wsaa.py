# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import datetime
import logging

from lxml import etree
from OpenSSL import crypto
from zeep import Client
from zeep.transports import Transport

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# WSAA endpoints
WSAA_URL = {
    "testing": "https://wsaahomo.afip.gov.ar/ws/services/LoginCms?WSDL",
    "production": "https://wsaa.afip.gov.ar/ws/services/LoginCms?WSDL",
}

# Token lifetime: request 12 hours, ARCA grants up to 24h
TOKEN_DURATION_HOURS = 12


class L10nArArcaWsaa(models.Model):
    _name = "l10n_ar.arca.wsaa"
    _description = "ARCA WSAA Authentication Service"

    @api.model
    def _get_or_refresh_token(self, certificate, service="wsfe"):
        """
        Get a valid WSAA token for the given service.
        If the cached token is still valid, return it.
        Otherwise, authenticate with ARCA and cache the new token.

        :param certificate: l10n_ar.arca.certificate record
        :param service: ARCA service name (e.g., 'wsfe', 'wsfex')
        :returns: dict with 'token' and 'sign' keys
        """
        certificate.ensure_one()

        if certificate.state != "active":
            raise UserError(
                _("Certificate '%s' is not active.", certificate.name)
            )

        # Check if cached token is still valid (with 10 min margin)
        now = fields.Datetime.now()
        if (
            certificate.wsaa_token
            and certificate.wsaa_sign
            and certificate.wsaa_token_expiration
            and certificate.wsaa_token_expiration > now + datetime.timedelta(minutes=10)
        ):
            return {
                "token": certificate.wsaa_token,
                "sign": certificate.wsaa_sign,
            }

        # Need to authenticate
        return self._authenticate(certificate, service)

    @api.model
    def _authenticate(self, certificate, service="wsfe"):
        """
        Perform WSAA LoginCMS authentication.

        Flow:
        1. Build a TRA (Ticket de Requerimiento de Acceso) XML
        2. Sign it with the private key + certificate using CMS (PKCS#7)
        3. Send the signed CMS to WSAA LoginCms endpoint
        4. Parse the response to extract Token and Sign

        :param certificate: l10n_ar.arca.certificate record
        :param service: ARCA service name
        :returns: dict with 'token' and 'sign' keys
        """
        certificate.ensure_one()

        # Step 1: Build TRA XML
        now = datetime.datetime.now(datetime.timezone.utc)
        generation_time = now - datetime.timedelta(minutes=10)
        expiration_time = now + datetime.timedelta(hours=TOKEN_DURATION_HOURS)

        tra_xml = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            "<loginTicketRequest version=\"1.0\">"
            "<header>"
            f"<uniqueId>{int(now.timestamp())}</uniqueId>"
            f"<generationTime>{generation_time.strftime('%Y-%m-%dT%H:%M:%S%z')}</generationTime>"
            f"<expirationTime>{expiration_time.strftime('%Y-%m-%dT%H:%M:%S%z')}</expirationTime>"
            "</header>"
            f"<service>{service}</service>"
            "</loginTicketRequest>"
        )

        _logger.info(
            "WSAA: Authenticating for service '%s' (cert: %s, env: %s)",
            service,
            certificate.name,
            certificate.environment,
        )

        # Step 2: Sign TRA with CMS (PKCS#7)
        cms_signed = self._sign_tra(certificate, tra_xml)

        # Step 3: Call WSAA LoginCms
        wsdl_url = WSAA_URL[certificate.environment]
        try:
            transport = Transport(timeout=30, operation_timeout=30)
            client = Client(wsdl_url, transport=transport)
            response = client.service.loginCms(cms_signed)
        except Exception as e:
            _logger.error("WSAA LoginCms failed: %s", str(e))
            raise UserError(
                _("WSAA authentication failed: %s", str(e))
            ) from e

        # Step 4: Parse response
        token, sign, expiration = self._parse_login_response(response)

        # Cache token in certificate
        certificate.sudo().write({
            "wsaa_token": token,
            "wsaa_sign": sign,
            "wsaa_token_expiration": expiration,
        })

        _logger.info(
            "WSAA: Authentication successful. Token valid until %s",
            expiration,
        )

        return {"token": token, "sign": sign}

    @api.model
    def _sign_tra(self, certificate, tra_xml):
        """
        Sign the TRA XML using PKCS#7 (CMS) with the certificate's
        private key and X.509 certificate.

        :param certificate: l10n_ar.arca.certificate record
        :param tra_xml: TRA XML string
        :returns: Base64-encoded CMS signature
        """
        # Load private key
        key_pem = base64.b64decode(certificate.private_key)
        pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, key_pem)

        # Load certificate
        cert_pem = base64.b64decode(certificate.certificate)
        x509_cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_pem)

        # Create PKCS#7 signed message
        bio_in = crypto._new_mem_buf(tra_xml.encode("utf-8"))
        pkcs7 = crypto._lib.PKCS7_sign(
            x509_cert._x509,
            pkey._pkey,
            crypto._ffi.NULL,
            bio_in,
            crypto._lib.PKCS7_BINARY | crypto._lib.PKCS7_NOATTR,
        )

        if pkcs7 == crypto._ffi.NULL:
            raise UserError(_("Failed to create PKCS#7 signature."))

        # Serialize to DER and encode as base64
        bio_out = crypto._new_mem_buf()
        crypto._lib.i2d_PKCS7_bio(bio_out, pkcs7)
        signed_data = crypto._bio_to_string(bio_out)

        return base64.b64encode(signed_data).decode("utf-8")

    @api.model
    def _parse_login_response(self, response):
        """
        Parse the WSAA loginCms XML response.

        Expected format:
        <loginTicketResponse version="1.0">
            <header>
                <source>...</source>
                <destination>...</destination>
                <uniqueId>...</uniqueId>
                <generationTime>...</generationTime>
                <expirationTime>...</expirationTime>
            </header>
            <credentials>
                <token>...</token>
                <sign>...</sign>
            </credentials>
        </loginTicketResponse>

        :returns: tuple (token, sign, expiration_datetime)
        """
        try:
            root = etree.fromstring(response.encode("utf-8"))
        except etree.XMLSyntaxError as e:
            raise UserError(
                _("Failed to parse WSAA response: %s", str(e))
            ) from e

        token = root.findtext(".//token")
        sign = root.findtext(".//sign")
        expiration_str = root.findtext(".//expirationTime")

        if not token or not sign:
            raise UserError(
                _("WSAA response missing token or sign credentials.")
            )

        # Parse expiration time
        expiration = fields.Datetime.now() + datetime.timedelta(
            hours=TOKEN_DURATION_HOURS
        )
        if expiration_str:
            try:
                # ARCA returns ISO format like 2025-01-01T12:00:00.000-03:00
                expiration = datetime.datetime.fromisoformat(expiration_str)
                # Convert to UTC naive datetime for Odoo
                expiration = expiration.astimezone(
                    datetime.timezone.utc
                ).replace(tzinfo=None)
            except (ValueError, TypeError):
                _logger.warning(
                    "Could not parse WSAA expiration time: %s",
                    expiration_str,
                )

        return token, sign, expiration
