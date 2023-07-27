# # -*- coding: utf-8 -*-
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.utils import ensure_db
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.exceptions import UserError, AccessDenied
from werkzeug.urls import url_encode
from odoo import http, tools, _
from odoo.http import request
from base64 import b64encode
import werkzeug
import psycopg2
import logging
import hashlib
import random
import string
import os

SIGN_UP_REQUEST_PARAMS = {'db', 'debug', 'token', 'message', 'error', 'scope', 'mode',
                          'redirect', 'redirect_hostname', 'first_name', 'nickname',
                          'en_first_name', 'en_nickname', 'father_name', 'mother_name',
                          'social_status', 'gender', 'age', 'birth_country_id', 'birth_state',
                          'birthday', 'country_id', 'state', 'city', 'address',
                          'mobile_number', 'email', 'party_affiliated', 'party_name',
                          'NGO_affiliated', 'NGO_name', 'volunteer_activities', 'study',
                          'university_id', 'college_id', 'department_id',
                          'partner_id', 'name', 'login', 'password', 'confirm_password', 'lang'}
_logger = logging.getLogger(__name__)


# mail_server_host = '172.16.10.54'
# db_user = 'postgres'
# db_password = 'postgresadmin123-'
# db_name1 = 'vmail'
# db_name2 = 'roundcubemail'
# domain = 'selanuss.org'


# mail_server_host = '192.168.20.20'
# db_user = 'postgres'
# db_password = 'PostGresCa123'
# db_name1 = 'vmail'
# db_name2 = 'roundcubemail'
domain = 'selanuss.org'


class NussAuthSignupHome(AuthSignupHome):

    def get_config_settings(self):
        config_settings = http.request.env['res.config.settings'].sudo().get_values()
        return config_settings

    def some_controller_method(self):
        config_settings = self.get_config_settings()
        self.mail_server_host = config_settings.get('mail_server_host')
        self.db_user = config_settings.get('db_user')
        self.db_password = config_settings.get('db_password')
        self.db_name1 = config_settings.get('db_name1')
        self.db_name2 = config_settings.get('db_name2')
        print('config_settings',config_settings)
        print('self.mail_server_host==>',self.mail_server_host)
        print('self.db_userself.db_user==>',self.db_user)
        print('self.db_password==>',self.db_password)
        print('self.db_name1==>',self.db_name1)
        print('self.db_name2==>',self.db_name2)

    def compute_cheap_hash(self, txt, length=5):
        hash = hashlib.sha1()
        hash.update(txt.encode('utf-8'))
        if hash.hexdigest()[:length] and len(hash.hexdigest()[:length]) >= length:
            return hash.hexdigest()[:length]
        # generating random strings
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))

    def generate_ssha512_password(self, p):
        p = str(p).strip()
        try:
            from hashlib import sha512
            salt = os.urandom(8)
            pw = sha512(p.encode('utf-8'))
            pw.update(salt)
            return '{SSHA512}' + b64encode(pw.digest() + salt).decode('utf-8')
        except ImportError as e:
            print(e)

    def insert_vmail_user(self, address, domain, name, password):
        self.some_controller_method()
        hashed_pass = self.generate_ssha512_password(password)
        connection = psycopg2.connect(host=self.mail_server_host, user=self.db_user,
                                      password=self.db_password, database=self.db_name1)

        maildir_hash = self.compute_cheap_hash(address)
        maildir = f"{domain}/{maildir_hash[0]}/{maildir_hash[1]}/{maildir_hash[2]}/" \
                  f"{maildir_hash[3]}/{maildir_hash[4]}/{address}/"
        query1 = f"""
                        INSERT INTO mailbox (username, password, name,
                             storagebasedirectory, storagenode, maildir,
                             quota, domain, active, passwordlastchange, created)
                        VALUES ('{address}@{domain}', '{hashed_pass}',
                                '{name}', '/var/vmail','vmail1', '{maildir}',
                                 '1024', '{domain}', '1', NOW(), NOW());
                        """
        query2 = f"""
                        INSERT INTO forwardings (address, forwarding, domain, dest_domain, is_forwarding)
                        VALUES ('{address}@{domain}', '{address}@{domain}','{domain}', '{domain}', 1);
                        """
        cursor = connection.cursor()
        try:
            cursor.execute(query1)
            connection.commit()
            cursor.execute(query2)
            connection.commit()
            return f'{address}@{domain}'
        except Exception as e:
            print(e)
            return False

    def insert_roundcubemail_user(self, address, domain):
        self.some_controller_method()  # Fetch configuration values
        connection1 = psycopg2.connect(host=self.mail_server_host, user=self.db_user,
                                      password=self.db_password, database=self.db_name2)
        query3 = f"""
                INSERT INTO users (username, mail_host, created, language)
                VALUES ('{address}@{domain}', '127.0.0.1',  NOW(), 'en_US');
                """
        query4 = f"""SELECT user_id from users WHERE USERNAME='{address}@{domain}';"""
        cursor1 = connection1.cursor()
        user_id = -1
        try:
            cursor1.execute(query3)
            connection1.commit()
            cursor1.execute(query4)
            user_id = cursor1.fetchall()
            if user_id:
                user_id = user_id[0][0]
            query5 = f"""
                    INSERT INTO identities (user_id, changed, del, standard, name, email, html_signature)
                    VALUES ({user_id},  NOW(), 0, 1, '', '{address}@{domain}', 0);
                    """
            cursor1.execute(query5)
            connection1.commit()
            return True

        except Exception as e:
            print(e)
            return False

    def check_address_exist(self, address_name):
        self.some_controller_method()  # Fetch configuration values

        connection = psycopg2.connect(host=self.mail_server_host, user=self.db_user,
                                      password=self.db_password, database=self.db_name1)

        query = f"""SELECT username FROM MAILBOX;"""
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        if result:
            for rec in result:
                if address_name in rec[0]:
                    return True
        return False

    def generate_random_uid(self, num_of_digit):
        random_id_number = ''.join([random.choice(string.digits) for n in range(num_of_digit)])
        return random_id_number

    def generate_address(self, name):
        clean_name = "".join(c.lower() for c in name if (c.isalpha() or c.isdigit()))
        num_of_alpha = 12
        num_of_digit = 0
        if len(clean_name) > num_of_alpha:
            clean_name = clean_name[0:num_of_alpha]
        auto_generate_address = clean_name + self.generate_random_uid(num_of_digit)
        while self.check_address_exist(auto_generate_address):
            num_of_alpha -= 1
            num_of_digit += 1
            clean_name = clean_name[0:num_of_alpha]
            auto_generate_address = clean_name + self.generate_random_uid(num_of_digit)
        return auto_generate_address

    def create_ired_email(self, address, name, password, domain):
        email = self.insert_vmail_user(address, domain, name, password)
        if email:
            if self.insert_roundcubemail_user(address, domain):
                return email

    @http.route('/my/student_email', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def student_email_info(self):
        user = request.env['res.users'].sudo().browse(request.uid)
        values = {}
        if user:
            values['login'] = user.login
        return request.render('ALTANMYA_NUSS_Affiliation.student_login_info_template', values)

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):

        qcontext = self.get_auth_signup_qcontext()

        _logger.info("qcontext in web/signup: get_auth_signup_qcontext() %s", qcontext)


        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':

            # Sela NUSS Additions
            qcontext_keys = list(qcontext.keys())
            if 'first_name' in qcontext_keys and 'nickname' in qcontext_keys:
                qcontext['name'] = qcontext['first_name'] + ' ' + qcontext['nickname']
            qcontext['domain'] = domain
            address_name = ''
            if 'en_first_name' in qcontext_keys and 'en_nickname' in qcontext_keys:
                address_name = qcontext['en_first_name'] + qcontext['en_nickname']
            address = self.generate_address(address_name)
            qcontext['login'] = self.create_ired_email(address, qcontext['name'], qcontext['password'],
                                                       qcontext['domain'])
            if len(list(request.params.items())) > 0:
                request.params.update({'login': qcontext['login']})
            ###################################################

            try:
                self.do_signup(qcontext)
                # Send an account creation confirmation email
                if qcontext.get('token'):
                    User = request.env['res.users']
                    user_sudo = User.sudo().search(
                        User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
                    )
                    template = request.env.ref('auth_signup.mail_template_user_signup_account_created',
                                               raise_if_not_found=False)
                    if user_sudo and template:
                        template.sudo().send_mail(user_sudo.id, force_send=True)

                # Sela NUSS Additions
                user = request.env['res.users'].sudo().browse(request.session.uid)
                if user:
                    partner = user.partner_id
                    partner.write({
                        'email': qcontext['email'],
                        'phone': qcontext['mobile_number'],
                        'country_id': int(qcontext['country_id']),
                        'city': qcontext['city'],
                    })
                    affiliated_vals = {
                        'user_id': user.id,
                        'partner_id': partner.id,
                        'first_name': qcontext['first_name'],
                        'nickname': qcontext['nickname'],
                        'en_first_name': qcontext['en_first_name'],
                        'en_nickname': qcontext['en_nickname'],
                        'full_name': qcontext['name'],
                        'father_name': qcontext['father_name'],
                        'mother_name': qcontext['mother_name'],
                        'social_status': qcontext['social_status'],
                        'gender': qcontext['gender'],
                        'age': qcontext['age'],
                        'birth_country_id': int(qcontext['birth_country_id']),
                        'birth_state': qcontext['birth_state'],
                        'birthday': qcontext['birthday'],
                        'country_id': qcontext['country_id'],
                        'state': qcontext['state'],
                        'city': qcontext['city'],
                        'address': qcontext['address'],
                        'mobile_number': qcontext['mobile_number'],
                        'email': qcontext['email'],
                        'student_email': qcontext['login'],
                        'party_affiliated': True if 'party_affiliated' in qcontext.keys() else False,
                        'party_name': qcontext['party_name'],
                        'NGO_affiliated': True if 'NGO_affiliated' in qcontext.keys() else False,
                        'NGO_name': qcontext['NGO_name'],
                        'volunteer_activities': qcontext['volunteer_activities'],
                        'study': qcontext['study'],
                        'university_id': int(qcontext['university_id']),
                        'college_id': int(qcontext['college_id']),
                        'department_id': int(qcontext['department_id'])
                    }
                    request.env['nuss.affiliated'].sudo().create(affiliated_vals)
                ###################################################
                return self.web_login(*args, **kw)
            except UserError as e:
                qcontext['error'] = e.args[0]
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.error("%s", e)
                    qcontext['error'] = _("Could not create a new account.")

        elif 'signup_email' in qcontext:
            user = request.env['res.users'].sudo().search(
                [('email', '=', qcontext.get('signup_email')), ('state', '!=', 'new')], limit=1)
            if user:
                return request.redirect('/web/login?%s' % url_encode({'login': user.login, 'redirect': '/web'}))
        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response

    @http.route('/web/reset_password', type='http', auth='public', website=True, sitemap=False)
    def web_auth_reset_password(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                if qcontext.get('token'):
                    self.do_signup(qcontext)
                    return self.web_login(*args, **kw)
                else:
                    login = qcontext.get('login')
                    assert login, _("No login provided.")
                    _logger.info(
                        "Password reset attempt for <%s> by user <%s> from %s",
                        login, request.env.user.login, request.httprequest.remote_addr)
                    request.env['res.users'].sudo().reset_password(login)
                    qcontext['message'] = _("Password reset instructions sent to your email")
            except UserError as e:
                qcontext['error'] = e.args[0]
            except SignupError:
                qcontext['error'] = _("Could not reset your password")
                _logger.exception('error when resetting password')
            except Exception as e:
                qcontext['error'] = str(e)

        elif 'signup_email' in qcontext:
            user = request.env['res.users'].sudo().search(
                [('email', '=', qcontext.get('signup_email')), ('state', '!=', 'new')], limit=1)
            if user:
                return request.redirect('/web/login?%s' % url_encode({'login': user.login, 'redirect': '/web'}))

        response = request.render('auth_signup.reset_password', qcontext)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response

    def get_auth_signup_config(self):
        """retrieve the module config (which features are enabled) for the login page"""
        get_param = request.env['ir.config_parameter'].sudo().get_param
        return {
            'disable_database_manager': not tools.config['list_db'],
            'signup_enabled': request.env['res.users']._get_signup_invitation_scope() == 'b2c',
            'reset_password_enabled': get_param('auth_signup.reset_password') == 'True',
        }

    def _get_nuss_auth_signup_qcontext(self, qcontext):
        options = http.request.env['nuss.affiliated'].fields_get(
            allfields=['study', 'age', 'gender', 'social_status'])

        # Selection Fields Options
        study_options = options['study']['selection']
        age_options = options['age']['selection']
        gender_options = options['gender']['selection']
        social_status_options = options['social_status']['selection']

        # Many2one Fields Options
        country_recs = request.env['res.country'].sudo().search([])
        countries_names = country_recs.mapped('name')
        countries_ids = country_recs.mapped('id')
        countries_options = [(_id, name) for name, _id in zip(countries_names, countries_ids)]

        universities_recs = request.env['in.university'].sudo().search([('type', '=', 'university')])
        universities_names = universities_recs.mapped('name')
        universities_ids = universities_recs.mapped('id')
        universities_options = [(_id, name) for name, _id in zip(universities_names, universities_ids)]

        colleges_recs = request.env['in.university'].sudo().search(
            [('type', 'in', ['collage', 'tech_inst', 'high_inst'])])
        colleges_names = colleges_recs.mapped('name')
        colleges_ids = colleges_recs.mapped('id')
        colleges_options = [(_id, name) for name, _id in zip(colleges_names, colleges_ids)]

        departments_recs = request.env['in.university'].sudo().search([('type', '=', 'department')])
        departments_names = departments_recs.mapped('name')
        departments_ids = departments_recs.mapped('id')
        departments_options = [(_id, name) for name, _id in zip(departments_names, departments_ids)]

        qcontext['study_options'] = study_options
        qcontext['age_options'] = age_options
        qcontext['gender_options'] = gender_options
        qcontext['social_status_options'] = social_status_options
        qcontext['countries_options'] = countries_options
        qcontext['universities_options'] = universities_options
        qcontext['colleges_options'] = []
        qcontext['departments_options'] = []

        return qcontext

    def get_auth_signup_qcontext(self):
        """ Shared helper returning the rendering context for signup and reset password """
        qcontext = {k: v for (k, v) in request.params.items() if k in SIGN_UP_REQUEST_PARAMS}
        qcontext.update(self.get_auth_signup_config())

        _logger.info("qcontext in get_auth_signup_qcontext   1 %s", qcontext)


        if not qcontext.get('token') and request.session.get('auth_signup_token'):
            qcontext['token'] = request.session.get('auth_signup_token')
        if qcontext.get('token'):
            try:
                # retrieve the user info (name, login or email) corresponding to a signup token
                token_infos = request.env['res.partner'].sudo().signup_retrieve_info(qcontext.get('token'))
                for k, v in token_infos.items():
                    qcontext.setdefault(k, v)
            except:
                qcontext['error'] = _("Invalid signup token")
                qcontext['invalid_token'] = True

        # Update qcontext values with nuss selection fields options
        qcontext = self._get_nuss_auth_signup_qcontext(qcontext)
        _logger.info("qcontext in get_auth_signup_qcontext   2%s", qcontext)

        return qcontext

    def _prepare_signup_values(self, qcontext):
        values = {key: qcontext.get(key) for key in ('login', 'name', 'password')}
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported_lang_codes = [code for code, _ in request.env['res.lang'].get_installed()]
        lang = request.context.get('lang', '')
        if lang in supported_lang_codes:
            values['lang'] = lang
        return values

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = self._prepare_signup_values(qcontext)
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()

    def _signup_with_values(self, token, values):
        login, password = request.env['res.users'].sudo().signup(values, token)
        request.env.cr.commit()  # as authenticate will use its own cursor we need to commit the current transaction
        pre_uid = request.session.authenticate(request.db, login, password)
        if not pre_uid:
            raise SignupError(_('Authentication Failed.'))

    @http.route('/web/get_related_collages', type='json', auth='none')
    def get_related_collages(self, university_id):
        collages_recs = request.env['in.university'].sudo().search(
            [('parent_id', '=', int(university_id)), ('type', 'in', ['collage', 'tech_inst', 'high_inst'])])
        collages_ids = collages_recs.mapped('id')
        collages_names = collages_recs.mapped('name')
        collages = [(_id, name) for name, _id in zip(collages_names, collages_ids)]
        return collages

    @http.route('/web/get_related_departments', type='json', auth='none')
    def get_related_departments(self, college_id):
        departments_recs = request.env['in.university'].sudo().search(
            [('parent_id', '=', int(college_id)), ('type', '=', 'department')])
        departments_ids = departments_recs.mapped('id')
        departments_names = departments_recs.mapped('name')
        departments = [(_id, name) for name, _id in zip(departments_names, departments_ids)]
        return departments
