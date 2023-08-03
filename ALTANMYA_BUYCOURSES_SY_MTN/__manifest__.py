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
    'name': "ALTANMYA BUYCOURSES SY MTN",
    'version': '1.0',
    'summary': """ALTANMYA BUYCOURSES SY MTN""",
    'description': """This Tanmya's module provides a system for NUSS platform.""",
    'category': 'Human Resources/Students Insurance',
    'author': 'ALTANMYA - TECHNOLOGY SOLUTIONS',
    'company': 'ALTANMYA - TECHNOLOGY SOLUTIONS Part of ALTANMYA GROUP',
    'website': "http://tech.altanmya.net",
    'depends': ['base', 'approvals', 'mail', 'website', 'portal', 'website_mail', 'web'],
    'data': [
        'views/payment_method.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'ALTANMYA_BUYCOURSES_SY_MTN/static/js/paymentC.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': -1000,
}
