from odoo import api, fields, models, _


class NussAffiliated(models.Model):
    _name = 'nuss.affiliated'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'NUSS Affiliated'
    _rec_name = 'full_name'

    @api.model
    def get_related_collages(self, *args, **kwargs):
        print("get_related_collages")
        university_id = int(args[0])
        collages_recs = self.env['in.university'].search(
            [('parent_id', '=', university_id), ('type', 'in', ['collage', 'tech_inst', 'high_inst'])])
        collages_ids = collages_recs.mapped('id')
        collages_names = collages_recs.mapped('name')
        collages = [(_id, name) for name, _id in zip(collages_names, collages_ids)]
        return collages

    @api.model
    def get_related_departments(self, *args, **kwargs):
        college_id = int(args[0])
        departments_recs = self.env['in.university'].search(
            [('parent_id', '=', college_id), ('type', '=', 'department')])
        departments_ids = departments_recs.mapped('id')
        departments_names = departments_recs.mapped('name')
        departments = [(_id, name) for name, _id in zip(departments_names, departments_ids)]
        return departments

    user_id = fields.Many2one('res.users', string=_('Affiliated User'))
    partner_id = fields.Many2one('res.partner', string=_('Affiliated Contact'))

    first_name = fields.Char(string=_('First Name In Arabic'))
    nickname = fields.Char(string=_('Nickname In Arabic'))

    en_first_name = fields.Char(string=_('First Name In English'))
    en_nickname = fields.Char(string=_('Nickname In English'))

    full_name = fields.Char(string=_('Full Name'), compute='_compute_full_name', store=True, readonly=False)
    father_name = fields.Char(string=_('Father Name'))
    mother_name = fields.Char(string=_('Mother Name'))

    social_status = fields.Selection(
        [('single', _('Single')),
         ('married', _('Married'))], string=_('Social Status'), default='single')
    gender = fields.Selection(
        [('male', _('Male')),
         ('female', _('Female'))], string=_('Gender'), default='male')
    age = fields.Selection(
        [('18_25', '18 -> 25'),
         ('26_35', '26 -> 35'),
         ('36_45', '36 -> 45'),
         ('46_55', '46 -> 55'),
         ('more_than_55', 'More Than 55')], string=_('Age'), default='18_25')

    birth_country_id = fields.Many2one('res.country', string=_('Birth Country'))
    birth_state = fields.Char(string=_('Birth State'))
    birthday = fields.Date(string=_('Birth Day'))

    country_id = fields.Many2one('res.country', string=_('Country Of Residence'))
    state = fields.Char(string=_('State'))
    city = fields.Char(string=_('City'))
    address = fields.Char(string=_('Address'))

    mobile_number = fields.Char(string=_('Mobile Number'))
    email = fields.Char(string=_('Email'))
    student_email = fields.Char(string=_('Student Email'), readonly=True)

    party_affiliated = fields.Boolean(string=_('Affiliated With A Party'), default=False)
    party_name = fields.Char(string=_('Party Name'))
    NGO_affiliated = fields.Boolean(string=_('Affiliated To An NGO'), default=False)
    NGO_name = fields.Char(string=_('NGO Name'))
    volunteer_activities = fields.Text(string=_('Volunteer Activities'))

    study = fields.Selection(
        [('first_year', _("First Year")),
         ('second_year', _("Second Year")),
         ('third_year', _("Third Year")),
         ('fourth_year', _("Fourth Year")),
         ('fifth_year', _("Fifth Year")),
         ('sixth_year', _("Sixth Year")),
         ("bachelor", _("Bachelor")),
         ("master", _("Master")),
         ("phd", _("Ph.D")),
         ("diploma", _("Diploma"))],
        string=_('Study'))
    university_id = fields.Many2one('in.university', string=_('University'), domain="[('type', '=', 'university')]")
    college_id = fields.Many2one('in.university', string=_('College'), domain="[('type', '=', 'collage')]")
    department_id = fields.Many2one('in.university', string=_('Department'), domain="[('type', '=', 'department')]")

    @api.depends('first_name', 'nickname')
    def _compute_full_name(self):
        for rec in self:
            if rec.nickname:
                rec.full_name = '%s %s' % (rec.first_name, rec.nickname)
            else:
                rec.full_name = rec.first_name

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.full_name))
        return result

