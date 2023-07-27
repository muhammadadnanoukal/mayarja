from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from odoo import api, fields, models, tools, SUPERUSER_ID, _, Command
from odoo.http import request, DEFAULT_LANG
from base64 import b64encode
import psycopg2
import logging
import os

_logger = logging.getLogger(__name__)


# mail_server_host = '172.16.10.54'
# db_user = 'postgres'
# db_password = 'postgresadmin123-'
# db_name1 = 'vmail'
# db_name2 = 'roundcubemail'
# domain = 'selanuss.org'

mail_server_host = '192.168.20.20'
db_user = 'postgres'
db_password = 'PostGresCa123'
db_name1 = 'vmail'
db_name2 = 'roundcubemail'
domain = 'selanuss.org'


class ResUsersInherit(models.Model):
    _inherit = 'res.users'

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

    def update_vmail_user_password(self, password, student_email):
        connection = psycopg2.connect(host=mail_server_host, user=db_user,
                                      password=db_password, database=db_name1)
        hashed_pass = self.generate_ssha512_password(password)
        query = f"""UPDATE mailbox SET password='{hashed_pass}' WHERE username='{student_email}';"""
        cursor = connection.cursor()
        try:
            cursor.execute(query)
            connection.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def _change_password(self, new_passwd):
        new_passwd = new_passwd.strip()
        if not new_passwd:
            raise UserError(_("Setting empty passwords is not allowed for security reasons!"))

        ip = request.httprequest.environ['REMOTE_ADDR'] if request else 'n/a'
        _logger.info(
            "Password change for %r (#%d) by %r (#%d) from %s",
             self.login, self.id,
             self.env.user.login, self.env.user.id,
             ip
        )
        self.password = new_passwd

        # Sela Nuss ( Update Student Email password in 'Roundcube' database)
        student_email = self.login
        if student_email:
            self.update_vmail_user_password(new_passwd, student_email)
        ###################################################################