from odoo import api, fields, models, _, tools
from werkzeug import urls


class PaymentMethod(models.Model):
    _name = 'in.payment.method'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Payment Methods'
    _order = 'name'

    image_256 = fields.Image(max_width=256, max_height=256, store=True, required=True)
    name = fields.Char('Name', required=True)
    type = fields.Selection([('mtn_syriatel', 'MTN / Syriatel Cash'),
                             ('bank', 'Bank')],
                            string='Payment Type',
                            required=True, default='bank')
    ms_type = fields.Selection([('mtn', 'MTN'),
                                ('syriatel', 'Syriatel')],
                               string='Choose One')
    account_number = fields.Char('Account Number')
    merchant_username = fields.Char('Username', required=True)
    merchant_password = fields.Char('Password', required=True)
    mobile = fields.Char('Mobile Number')
    e_payment_link = fields.Char('Electronic Payment Link')
    active_account = fields.Boolean('Active Account', default=False)

    @api.onchange('type')
    def _onchange_type(self):
        self.ms_type = ''
        self.mobile = ''
        self.active_account = False

    @api.onchange('active_account')
    def _onchange_active_account(self):
        if self.active_account:
            mtn_syriatel_recs = self.env['in.payment.method'].search([('ms_type', '=', self.type), ('active_account', '=', True)])
            for rec in mtn_syriatel_recs:
                if rec.id != self.id:
                    rec.write({'active_account': False})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'active_account' in vals and vals.get('active_account'):
                mtn_syriatel_recs = self.env['in.payment.method'].search(
                    [('ms_type', '=', vals.get('ms_type')), ('active_account', '=', True)])
                for rec in mtn_syriatel_recs:
                    rec.write({'active_account': False})
        return super(PaymentMethod, self).create(vals_list)

    def write(self, vals):
        if 'active_account' in vals and vals.get('active_account'):
            mtn_syriatel_recs = self.env['in.payment.method'].search(
                [('ms_type', '=', self.ms_type), ('active_account', '=', True)])
            for rec in mtn_syriatel_recs:
                rec.write({'active_account': False})
        return super(PaymentMethod, self).write(vals)
