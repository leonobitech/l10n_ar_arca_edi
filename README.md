# l10n_ar_arca_edi

**Odoo 19 Community** - Argentina ARCA Electronic Invoicing (WSAA / WSFEv1)

## Overview

This addon integrates Odoo Community Edition with ARCA (Agencia de Recaudación y Control Aduanero, formerly AFIP) web services for electronic invoicing in Argentina.

## Features

- **Certificate Management**: Generate RSA private keys and CSR (Certificate Signing Request) directly from Odoo
- **WSAA Integration**: Automatic authentication with ARCA via CMS (PKCS#7) signed tickets
- **WSFEv1 Integration**: Electronic invoice authorization and CAE (Código de Autorización Electrónico) generation
- **RG 5616 Compliant**: Includes customer IVA condition reporting (mandatory since April 2025)
- **Dual Environment**: Support for both testing (homologación) and production environments
- **Auto CAE on Post**: Automatic CAE request when posting invoices
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
All included in the official Odoo Docker image:
- `cryptography`
- `pyOpenSSL`
- `zeep`
- `lxml`

## Installation

1. Copy the `l10n_ar_arca_edi` folder to your Odoo addons path
2. Update the addons list: Settings > Apps > Update Apps List
3. Install "Argentina - ARCA Electronic Invoicing"

## Configuration

### 1. Create Certificate

Go to **Accounting > Configuration > ARCA > Certificates**:

1. Create a new certificate record with your CUIT and environment
2. Click **"Generate Key & CSR"**
3. Copy the CSR content

### 2. Get Certificate from ARCA

**Testing (Homologación):**
- Go to ARCA portal > WSASS (Autogestión Certificados Homologación)
- Create a new certificate using your CSR

**Production:**
- Go to ARCA portal > Administrador de Relaciones de Clave Fiscal
- Access "Administración de Certificados Digitales"
- Create a new certificate using your CSR

### 3. Upload Certificate

Back in Odoo, click **"Upload Certificate"** and upload the `.crt` file from ARCA.

### 4. Configure Company

Go to **Settings > Accounting** and select the active ARCA certificate.

### 5. Configure Journal

On your sales journal, ensure:
- **ARCA POS System** is set to "Online Invoice"
- **ARCA Electronic Invoicing** is enabled

## Usage

Once configured, CAE is automatically requested when posting invoices. You can also manually request CAE using the **"Request CAE"** button on posted invoices.

## ARCA Web Services

| Service | URL (Testing) | URL (Production) |
|---------|---------------|-------------------|
| WSAA | wsaahomo.afip.gov.ar | wsaa.afip.gov.ar |
| WSFEv1 | wswhomo.afip.gov.ar | servicios1.afip.gov.ar |

## License

LGPL-3 - See [LICENSE](LICENSE) file.

## Author

[Leonobitech](https://leonobitech.com)

## Contributing

Contributions are welcome! Please submit pull requests to the [GitHub repository](https://github.com/leonobitech/l10n_ar_arca_edi).
