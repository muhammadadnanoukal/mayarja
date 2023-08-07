# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('syriatell12', 'Syriatell12')], ondelete={'syriatell12': 'set default'})
    test = fields.Char('test')
    #=== COMPUTE METHODS ===#

    @api.depends('code')
    def _compute_journal_id(self):
        for provider in self:
            payment_method = self.env['account.payment.method.line'].search([
                ('journal_id.company_id', '=', provider.company_id.id),
                ('code', '=', provider.code)
            ], limit=1)
            print('==>payment_method', payment_method)
            if payment_method:
                print('if payment_method',payment_method)
                provider.journal_id = payment_method.journal_id
            else:
                print('else payment_method',  provider.journal_id)
                provider.journal_id = False

    @api.depends('code')
    def _compute_view_configuration_fields(self):
        """ Override of payment to hide the credentials page.

        :return: None
        """
        super()._compute_view_configuration_fields()
        self.filtered(lambda p: p.code == 'syriatell12').show_credentials_page = False

    def _compute_feature_support_fields(self):
        """ Override of `payment` to enable additional features. """
        super()._compute_feature_support_fields()
        self.filtered(lambda p: p.code == 'syriatell12').update({
            'support_fees': True,
            'support_manual_capture': True,
            'support_refund': 'partial',
            'support_tokenization': True,
        })

    # === CONSTRAINT METHODS ===#

    @api.constrains('state', 'code')
    def _check_provider_state(self):
        if self.filtered(lambda p: p.code == 'syriatell12' and p.state not in ('test', 'disabled')):
            raise UserError(_("syriatell12 providers should never be enabled."))
