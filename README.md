# l10n_ar_arca_edi

**Odoo 19 Community** - Argentina ARCA Electronic Invoicing (WSAA / WSFEv1)

## Overview

This addon integrates Odoo Community Edition with ARCA (Agencia de Recaudación y Control Aduanero, formerly AFIP) web services for electronic invoicing in Argentina.

## Features

- **Certificate Management**: Generate RSA private keys and CSR (Certificate Signing Request) directly from Odoo Settings
- **WSAA Integration**: Automatic authentication with ARCA via CMS (PKCS#7) signed tickets
- **WSFEv1 Integration**: Electronic invoice authorization and CAE (Código de Autorización Electrónico) generation
- **RG 5616 Compliant**: Includes customer IVA condition reporting (mandatory since April 2025)
- **Dual Environment**: Support for both testing (homologación) and production environments
- **Auto CAE on Post**: Automatic CAE request when posting invoices
- **Token Caching**: WSAA tokens are cached and reused until expiration
- **Certificate Expiration**: Automatic monitoring via cron job

## Supported Documents

| Type | A | B | C | E (Export) |
|------|---|---|---|------------|
| Factura | ✅ | ✅ | ✅ | ✅ |
| Nota de Débito | ✅ | ✅ | ✅ | ✅ |
| Nota de Crédito | ✅ | ✅ | ✅ | ✅ |

## Requirements

### Odoo Modules
- `l10n_ar` (Argentina Accounting Localization)
- `account_edi` (Electronic Data Interchange base)

### Python Libraries
All included in the official Odoo 19 Docker image:
- `cryptography`
- `zeep`
- `lxml`

## Installation

1. Copy the `l10n_ar_arca_edi` folder to your Odoo addons path
2. Update the addons list: **Settings > Apps > Update Apps List**
3. Search and install **"Argentina - ARCA Electronic Invoicing"**

## Setup Guide

Everything is configured from **Settings > Accounting > ARCA Electronic Invoicing** (top of the page).

### Step 1: Create Certificate (in Odoo)

1. Go to **Settings > Accounting**
2. In the **ARCA Electronic Invoicing** section, click **"Create Certificate"**
3. Fill in the name (e.g., `MyCompany-Testing`), select company and environment
4. Click **"Create Certificate"**
5. Click **"Generate Key & CSR"** — this generates your private key and CSR

### Step 2: Create DN in ARCA Portal

Go to the ARCA portal to register your certificate:

**Testing (Homologación):**
- URL: https://wsass-homo.afip.gob.ar/wsass/portal/main.aspx
- Login with your CUIT and clave fiscal

**Production:**
- Go to ARCA portal > Administrador de Relaciones de Clave Fiscal
- Access "Administración de Certificados Digitales"

Once logged in:

1. Click **"Nuevo Certificado"** (or "Crear DN y certificado")
2. **Nombre simbólico del DN**: Enter a name (e.g., `MyCompanyTesting`)
3. **CUIT del contribuyente**: Should be pre-filled with your CUIT
4. **Solicitud de certificado (CSR)**: Go back to Odoo, copy the CSR content using the copy button, and paste it here
5. Click **"Crear DN y obtener certificado"**
6. In the **Resultado** section, copy the certificate content and save it as a `.crt` file

### Step 3: Authorize wsfe Service in ARCA

Still in the ARCA portal:

1. Click **"Crear autorización a servicio"** in the left menu
2. **Nombre simbólico del DN**: Select the DN you just created
3. **CUIT representado**: Your CUIT
4. **Servicio**: Select **"wsfe - Facturación Electrónica"**
5. Click **"Crear autorización de acceso"**

> **Important**: Without this step, the Test Connection will fail with "Computador no autorizado a acceder al servicio".

### Step 4: Upload Certificate (in Odoo)

1. Back in Odoo Settings, click **"Upload Certificate"**
2. Upload the `.crt` file you saved from ARCA
3. Click **"Upload"**

### Step 5: Test Connection

1. Click **"Test Connection"**
2. You should see a green toast: "Connection Successful. WSAA authentication successful."

That's it! Your Odoo is now connected to ARCA.

### Step 6: Configure Journal

On your sales journal (**Accounting > Configuration > Journals**):
- Set **ARCA POS System** to "Online Invoice"
- Enable **ARCA Electronic Invoicing**

## Usage

Once configured, CAE is automatically requested when posting invoices. You can also manually request CAE using the **"Request CAE"** button on posted invoices.

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    Odoo      │     │    WSAA      │     │   WSFEv1     │
│  (this addon)│────▶│ (Auth Token) │────▶│ (CAE Request)│
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │                      │
       │  CMS/PKCS#7        │  Token + Sign        │  CAE + Vto
       │  signed TRA        │                      │
       ▼                    ▼                      ▼
  Private Key +        Login Ticket           Invoice Data
  Certificate          Response               + Authorization
```

### Authentication Flow (WSAA)

1. Build a TRA (Ticket de Requerimiento de Acceso) XML with timestamps in Argentina timezone (-03:00)
2. Sign it with CMS/PKCS#7 using the private key and certificate
3. Send the signed CMS to WSAA `loginCms` endpoint
4. Parse response to extract Token and Sign
5. Cache token until expiration (typically 12 hours)

## ARCA Web Services

| Service | Testing (Homologación) | Production |
|---------|----------------------|------------|
| WSAA | wsaahomo.afip.gov.ar | wsaa.afip.gov.ar |
| WSFEv1 | wswhomo.afip.gov.ar | servicios1.afip.gov.ar |
| WSASS Portal | wsass-homo.afip.gob.ar | (via clave fiscal portal) |

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| "No se ha podido interpretar el XML contra el SCHEMA" | Timezone format wrong in TRA XML | Fixed in v1.0 — uses ISO format with colon (-03:00) |
| "Computador no autorizado a acceder al servicio" | wsfe service not authorized | Go to ARCA portal > "Crear autorización a servicio" > select wsfe |
| "El CEE ya posee un TA válido" | Token already active | Not an error — token is cached and valid. Click Test Connection again |
| Upload certificate fails | `not_valid_before_utc` attribute error | Fixed in v1.0 — uses `not_valid_before` (compatible with Odoo 19 cryptography version) |

## License

LGPL-3 - See [LICENSE](LICENSE) file.

## Author

[Leonobitech](https://leonobitech.com)

## Contributing

Contributions are welcome! Please submit pull requests to the [GitHub repository](https://github.com/leonobitech/l10n_ar_arca_edi).
