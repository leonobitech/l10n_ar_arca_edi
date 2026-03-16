# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Argentina - ARCA Electronic Invoicing",
    "version": "19.0.1.0.0",
    "category": "Accounting/Localizations",
    "summary": "Electronic invoicing integration with ARCA (ex-AFIP) for Argentina",
    "description": """
Argentina ARCA Electronic Invoicing
====================================

This module integrates Odoo with ARCA (Agencia de Recaudación y Control Aduanero)
web services for electronic invoicing in Argentina.

Features:
---------
* Generate CSR (Certificate Signing Request) from Odoo
* Manage digital certificates for ARCA authentication
* WSAA: Authentication and authorization via CMS (Cryptographic Message Syntax)
* WSFEv1: Electronic invoice authorization (CAE)
* Support for both testing (homologación) and production environments

Requirements:
-------------
* OpenSSL (via pyOpenSSL / cryptography)
* zeep (SOAP client)
* lxml

Supported document types:
-------------------------
* Facturas A, B, C, E
* Notas de Crédito
* Notas de Débito

ARCA Web Services:
------------------
* WSAA - Web Service de Autenticación y Autorización
* WSFEv1 - Web Service de Factura Electrónica v1
    """,
    "author": "Leonobitech",
    "website": "https://github.com/leonobitech/l10n_ar_arca_edi",
    "license": "LGPL-3",
    "countries": ["ar"],
    "depends": [
        "l10n_ar",
        "account_edi",
    ],
    "external_dependencies": {
        "python": [
            "cryptography",
            "zeep",
            "lxml",
        ],
    },
    "data": [
        "security/ir.model.access.csv",
        "data/paperformat.xml",
        "wizards/l10n_ar_arca_certificate_wizard_views.xml",
        "views/l10n_ar_arca_certificate_views.xml",
        "views/res_config_settings_views.xml",
        "views/account_move_views.xml",
        "views/account_journal_views.xml",
        "reports/report_invoice.xml",
        "data/ir_cron_data.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "l10n_ar_arca_edi/static/src/scss/arca_badge.scss",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": False,
}
