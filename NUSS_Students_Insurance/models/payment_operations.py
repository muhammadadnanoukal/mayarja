from odoo import api, fields, models, _, tools
from werkzeug import urls


class PaymentOperation(models.Model):
    _name = 'in.payment.operation'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Payment Operations'
    _order = 'transaction_id'

    transaction_id = fields.Text('Transaction ID', required=True)
    customer_MSISDN = fields.Char('Customer MSISDN', required=True)
    merchant_MSISDN = fields.Char('Merchant MSISDN', required=True)
    amount = fields.Char('Amount', required=True)
    token = fields.Text('Token')
    transaction_time = fields.Datetime('Transaction Time', required=True)
    state = fields.Selection(
        [('pending', "Pending"),
         ('paid', "Paid")],
        string='State', required=True)
    payment_method_id = fields.Many2one('in.payment.method', 'Payment Method', required=True)

    def name_get(self):
        result = []
        for operation in self:
            result.append((operation.id, operation.transaction_id))
        return result