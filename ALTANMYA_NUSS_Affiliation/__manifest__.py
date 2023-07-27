# -*- coding: utf-8 -*-
{
    'name': "ALTANMYA NUSS Affiliation",
    'summary': """NUSS Affiliation""",
    'description': """NUSS Affiliation""",
    'author': 'ALTANMYA - TECHNOLOGY SOLUTIONS',
    'company': 'ALTANMYA - TECHNOLOGY SOLUTIONS Part of ALTANMYA GROUP',
    'website': "http://tech.altanmya.net",
    'category': 'Uncategorized',
    'version': '1.0',
    'depends': ['web', 'website', 'portal', 'auth_signup', 'base', 'base_setup', 'NUSS_Students_Insurance'],
    'data': [
        'views/nuss_affiliated_views.xml',
        'views/menus_views.xml',
        'views/nuss_signup_templates.xml',
        'views/login_info_templates.xml',
        'views/res_config_settings.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_frontend': [
            'ALTANMYA_NUSS_Affiliation/static/src/js/nuss_affiliation_form.js'
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': -100000,
}
