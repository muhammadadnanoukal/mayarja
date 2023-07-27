from odoo import api, fields, models, _, tools
from werkzeug import urls


class Messaging(models.Model):
    _name = 'in.messaging'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Messaging'
    _order = 'name'

    name = fields.Char('Name', required=True, store=True)
    type = fields.Selection([('rejected', 'Rejection Message'),
                             ('approved', 'Approval Message')],
                            required=True)


class MessagingAPI(models.Model):
    _name = 'in.messaging.api'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Messaging API'
    _order = 'username'

    username = fields.Char('Username', required=True, store=True)
    password = fields.Char('Password', required=True, store=True)
    sender = fields.Char('Sender', required=True, store=True)
    active_account = fields.Boolean('Active Account', default=False)

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, rec.username))
        return res

    @api.onchange('active_account')
    def _onchange_active_account(self):
        if self.active_account:
            messaging_apis = self.env['in.messaging.api'].search([('active_account', '=', True)])
            for rec in messaging_apis:
                if rec.id != self.id:
                    rec.write({'active_account': False})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'active_account' in vals and vals.get('active_account'):
                messaging_apis = self.env['in.messaging.api'].search([('active_account', '=', True)])
                for rec in messaging_apis:
                    rec.write({'active_account': False})
        return super(MessagingAPI, self).create(vals_list)

    def write(self, vals):
        if 'active_account' in vals and vals.get('active_account'):
            messaging_apis = self.env['in.messaging.api'].search([('active_account', '=', True)])
            for rec in messaging_apis:
                rec.write({'active_account': False})
        return super(MessagingAPI, self).write(vals)