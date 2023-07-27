from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResConfigSettingsNuss(models.TransientModel):
    _inherit = 'res.config.settings'

    mail_server_host = fields.Char('mail server host', store=True)
    db_user = fields.Char('database user')
    db_password = fields.Char('database password')
    db_name1 = fields.Char('database name1')
    db_name2 = fields.Char('database name1')

    def set_values(self):
        res = super(ResConfigSettingsNuss, self).set_values()
        self.env['ir.config_parameter'].set_param('ALTANMYA_NUSS_Affiliation.mail_server_host',
                                                  self.mail_server_host)
        self.env['ir.config_parameter'].set_param('ALTANMYA_NUSS_Affiliation.db_user',
                                                  self.db_user)
        self.env['ir.config_parameter'].set_param('ALTANMYA_NUSS_Affiliation.db_password',
                                                  self.db_password)
        self.env['ir.config_parameter'].set_param('ALTANMYA_NUSS_Affiliation.db_name1',
                                                  self.db_name1)
        self.env['ir.config_parameter'].set_param('ALTANMYA_NUSS_Affiliation.db_name2',
                                                  self.db_name2)

        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettingsNuss, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        mail_server_host = ICPSudo.get_param('ALTANMYA_NUSS_Affiliation.mail_server_host')
        db_user = ICPSudo.get_param('ALTANMYA_NUSS_Affiliation.db_user')
        db_password = ICPSudo.get_param('ALTANMYA_NUSS_Affiliation.db_password')
        db_name1 = ICPSudo.get_param('ALTANMYA_NUSS_Affiliation.db_name1')
        db_name2 = ICPSudo.get_param('ALTANMYA_NUSS_Affiliation.db_name2')
        res.update(
            mail_server_host=mail_server_host,
            db_user=db_user,
            db_password=db_password,
            db_name1=db_name1,
            db_name2=db_name2,
        )
        return res
