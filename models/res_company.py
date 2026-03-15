# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_ar_arca_certificate_id = fields.Many2one(
        "l10n_ar.arca.certificate",
        string="ARCA Certificate",
        domain="[('company_id', '=', id), ('state', '=', 'active')]",
        help="Active ARCA digital certificate for electronic invoicing.",
    )
