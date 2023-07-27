from odoo import api, fields, models, _, tools
from werkzeug import urls
from odoo.osv.expression import AND, OR


class University(models.Model):
    _name = 'in.university'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'University'
    _order = 'name'
    _rec_name = 'complete_name'

    name = fields.Char('Name', required=True)
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', recursive=True, store=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    parent_university_id = fields.Many2one('in.university', string='University Related To',
                                           domain="[('type', '=', 'university')]")
    parent_collage_id = fields.Many2one('in.university', string='Collage/Institute Related To',
                                        domain="['|', '|', ('type', '=', 'collage'), ('type', '=', 'tech_inst'), ('type', '=', 'high_inst')]")
    parent_id = fields.Many2one('in.university', compute='_compute_parent_id', store=True)
    related_to_self_count = fields.Integer(compute='_compute_related_to_self_count')

    @api.depends('name')
    def _compute_parent_id(self):
        if self.parent_collage_id.id:
            self.parent_id = self.parent_collage_id.id
            return
        if self.parent_university_id.id:
            self.parent_id = self.parent_university_id.id
            return
        self.parent_id = None

    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone Number')
    mobile = fields.Char(string='Mobile Number')
    website = fields.Char('Website Link')
    type = fields.Selection([('university', 'University'),
                             ('collage', 'Collage'),
                             ('high_inst', 'Higher Institute'),
                             ('tech_inst', 'Technical Institute'),
                             ('department', 'Department')],
                            required=True, default='university')
    emc_id = fields.Many2one('expenses.management.company', string='Expenses Management Company', store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('website'):
                vals['website'] = self._clean_website(vals['website'])
        return super(University, self).create(vals_list)

    def _clean_website(self, website):
        url = urls.url_parse(website)
        if not url.scheme:
            if not url.netloc:
                url = url.replace(netloc=url.path, path='')
            website = url.replace(scheme='http').to_url()
        return website

    def name_get(self):
        if not self.env.context.get('hierarchical_naming', True):
            return [(record.id, record.name) for record in self]
        return super(University, self).name_get()

    @api.model
    def name_create(self, name):
        return self.create({'name': name}).name_get()[0]

    @api.depends('name')
    def _compute_complete_name(self):
        for university in self:
            if university.parent_id:
                university.complete_name = '%s / %s' % (university.parent_id.complete_name, university.name)
            else:
                university.complete_name = university.name

    @api.depends('complete_name')
    def _compute_related_to_self_count(self):
        for rec in self:
            rec.related_to_self_count = len(self.env['in.university'].search([('parent_id', '=', self.id)]))

    def action_view_related(self):
        self.ensure_one()
        action = {
            'name': 'Related',
            'res_model': 'in.university',
            'type': 'ir.actions.act_window',
        }
        recs = self.env['in.university'].search([('parent_id', '=', self.id)])
        if self.related_to_self_count == 1:
            action['res_id'] = recs[0].id
            action['view_mode'] = 'form'
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', recs.ids)]
        return action

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
        print("get_related_departments")
        college_id = int(args[0])
        departments_recs = self.env['in.university'].search(
            [('parent_id', '=', college_id), ('type', '=', 'department')])
        departments_ids = departments_recs.mapped('id')
        departments_names = departments_recs.mapped('name')
        departments = [(_id, name) for name, _id in zip(departments_names, departments_ids)]
        return departments
