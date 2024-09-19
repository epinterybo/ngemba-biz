# -*- coding: utf-8 -*-
{
    'name': 'YBO POS Close POS',
    'summary': 'Close POS Extended for POS',
    'description': '',
    'version': '1.0',
    'license': 'LGPL-3',
    'category': 'tools',
    'author': "YBO Services",
    'maintainer': 'YBO Services',
    'website': "https://www.ybo-services.com",
    'depends': ['web', 'base', 'point_of_sale'],
    'data': [
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'ybo_pos_close_pos/static/src/js/*.js',
            'ybo_pos_close_pos/static/src/xml/*.xml',
            'ybo_pos_close_pos/static/src/css/*.scss',
        ]
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}
