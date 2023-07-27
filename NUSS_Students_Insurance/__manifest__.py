# -*- coding: utf-8 -*-
###################################################################################
#
#    ALTANMYA - TECHNOLOGY SOLUTIONS
#    Copyright (C) 2022-TODAY ALTANMYA - TECHNOLOGY SOLUTIONS Part of ALTANMYA GROUP.
#    ALTANMYA - NUSS Students Insurance Module.
#    Author: ALTANMYA for Technology(<https://tech.altanmya.net>)
#
#    This program is Licensed software: you can not modify
#   #
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################
{
    'name': "ALTANMYA NUSS Students Insurance",
    'version': '1.0',
    'summary': """NU1SS Students Insurance""",
    'description': """This Tanmya's module provides a system for NUSS platform,
                    directed to the students to register their insurance requests.""",
    'category': 'Human Resources/Students Insurance',
    'author': 'ALTANMYA - TECHNOLOGY SOLUTIONS',
    'company': 'ALTANMYA - TECHNOLOGY SOLUTIONS Part of ALTANMYA GROUP',
    'website': "http://tech.altanmya.net",
    'depends': ['base', 'approvals', 'mail', 'website', 'portal', 'website_mail', 'web'],
    'data': [
        'data/approval_category_insurance.xml',
        'data/data.xml',
        # 'data/website_dropdown_menu.xml',
        'views/universities_views.xml',
        'views/insurance_request_views.xml',
        'views/messaging_views.xml',
        'views/expenses_management_company_views.xml',
        'views/expenses_management_company_templates.xml',
        'views/payment_methods_views.xml',
        'views/approval_request_views.xml',
        'views/approval_category_views.xml',
        'views/insurance_request_templates.xml',
        'views/payment_operations_views.xml',
        'views/payment_operation_templates.xml',
        'views/portal_messages_templates.xml',
        'views/menus_and_actions_views.xml',
        'views/payment_methods_templates.xml',
        'views/insurance_type_views.xml',
        'views/insurance_type_templates.xml',
        'views/insurance_card_templates.xml',
        # 'views/insurance_card_link.xml',
        'views/portal_my_requests.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_frontend': [
            'NUSS_Students_Insurance/static/src/scss/insurance_card_styles.scss',
            'NUSS_Students_Insurance/static/src/css/insurance_styles.css',
            'NUSS_Students_Insurance/static/src/js/insurance_request_form.js',
            'NUSS_Students_Insurance/static/src/xml/success_message.xml',
            'NUSS_Students_Insurance/static/src/xml/failure_message.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': -1000,
}
