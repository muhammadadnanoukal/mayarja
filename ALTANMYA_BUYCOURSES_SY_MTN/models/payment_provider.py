# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('syriatell12', 'Syriatell12')], ondelete={'syriatell12': 'set default'})
    test = fields.Char('test')
    merchant_username_two = fields.Char(
        string="merchant_username",
        help="The public business merchant_username solely used to identify the account with syriatell cash",
        required_if_provider='syriatell12')
    merchant_password = fields.Char(string="Merchant Password")
    mobile = fields.Char(string="mobile")

    #=== COMPUTE METHODS ===#

    @api.depends('code')
    def _compute_journal_id(self):

        for provider in self:
            print('==>provider', provider)
            print('==>provider.code', provider.code)
            print('==>provider.company_id.id', provider.company_id.id)
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

    @api.model
    def _remove_provider(self, code):
        """ Override of `payment` to delete the payment method of the provider. """
        super()._remove_provider(code)
        self._get_provider_payment_method(code).unlink()




    @api.depends('code')
    def _compute_view_configuration_fields(self):
        """ Override of payment to hide the credentials page.

        :return: None
        """
        super()._compute_view_configuration_fields()
        self.filtered(lambda p: p.code == 'syriatell12').show_credentials_page = True

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

    @api.model
    def _get_default_payment_method_id(self, code):
        provider_payment_method = self._get_provider_payment_method(code)
        if provider_payment_method:
            return provider_payment_method.id
        return self.env.ref('account.account_payment_method_manual_in').id

    @api.model
    def _get_provider_payment_method(self, code):
        return self.env['account.payment.method'].search([('code', '=', code)], limit=1)

    # === BUSINESS METHODS ===#

    @api.model
    def _setup_provider(self, code):
        """ Override of `payment` to create the payment method of the provider. """
        super()._setup_provider(code)
        self._setup_payment_method(code)


    @api.model
    def _setup_payment_method(self, code):
        if code not in ('none', 'custom') and not self._get_provider_payment_method(code):
            providers_description = dict(self._fields['code']._description_selection(self.env))
            self.env['account.payment.method'].create({
                'name': providers_description[code],
                'code': code,
                'payment_type': 'inbound',
            })

    @api.model
    def _remove_provider(self, code):
        """ Override of `payment` to delete the payment method of the provider. """
        super()._remove_provider(code)
        self._get_provider_payment_method(code).unlink()



    def button_immediate_install(self):
        """ Install the module and reload the page.

        Note: `self.ensure_one()`

        :return: The action to reload the page.
        :rtype: dict
        """
        if self.module_id and self.module_state != 'installed':
            self.module_id.button_immediate_install()
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

    @api.depends('code')
    def _compute_view_configuration_fields(self):
        """ Compute the view configuration fields based on the provider.

        View configuration fields are used to hide specific elements (notebook pages, fields, etc.)
        from the form view of payment providers. These fields are set to `True` by default and are
        as follows:

        - `show_credentials_page`: Whether the "Credentials" notebook page should be shown.
        - `show_allow_tokenization`: Whether the `allow_tokenization` field should be shown.
        - `show_allow_express_checkout`: Whether the `allow_express_checkout` field should be shown.
        - `show_payment_icon_ids`: Whether the `payment_icon_ids` field should be shown.
        - `show_pre_msg`: Whether the `pre_msg` field should be shown.
        - `show_pending_msg`: Whether the `pending_msg` field should be shown.
        - `show_auth_msg`: Whether the `auth_msg` field should be shown.
        - `show_done_msg`: Whether the `done_msg` field should be shown.
        - `show_cancel_msg`: Whether the `cancel_msg` field should be shown.

        For a provider to hide specific elements of the form view, it must override this method and
        set the related view configuration fields to `False` on the appropriate `payment.provider`
        records.

        :return: None
        """
        self.update({
            'show_credentials_page': True,
            'show_allow_tokenization': True,
            'show_allow_express_checkout': True,
            'show_payment_icon_ids': True,
            'show_pre_msg': True,
            'show_pending_msg': True,
            'show_auth_msg': True,
            'show_done_msg': True,
            'show_cancel_msg': True,
        })
