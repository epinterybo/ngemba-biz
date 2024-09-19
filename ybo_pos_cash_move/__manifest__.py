# -*- coding: utf-8 -*-

{
    'name': 'YBO POS Cash Move',
    'summary': 'Bill counting for POS',
    'description': 'Adds bill counting elements to the POS Cash In & Cash Out',
    'version': '1.01',
    'license': 'LGPL-3',
    'category': 'tools',
    'author': "YBO Services",
    'maintainer': 'YBO Services',
    'website': "https://www.ybo-services.com",
    'depends': ['web', 'base', 'point_of_sale',"ybo_pos_cheque_info"],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_cash_report_views.xml',
        'views/pos_simple_count_views.xml',
        'report/ir_actions_report.xml',
        'report/pos_cash_move_report.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'ybo_pos_cash_move/static/src/js/*.js',
            'ybo_pos_cash_move/static/src/xml/*.xml',
            'ybo_pos_cash_move/static/src/css/*.scss',
            'ybo_pos_cash_move/static/src/img/*.png',
        ]
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}
