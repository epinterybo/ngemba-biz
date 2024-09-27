{
    'name': 'YBO POS Cash Opening Popup',
    'summary': 'Cash Opening Extended for POS',
    'description': '',
    'version': '1.0',
    'license': 'LGPL-3',
    'category': 'tools',
    'author': "YBO Services",
    'maintainer': 'YBO Services',
    'website': "https://www.ybo-services.com",
    'depends': ['web', 'base', 'point_of_sale', 'ybo_pos_cash_move'],
    'data': [
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'ybo_pos_cash_opening_popup/static/src/js/*.js',
            'ybo_pos_cash_opening_popup/static/src/xml/*.xml',
            'ybo_pos_cash_opening_popup/static/src/css/*.scss',
        ]
    },
    'installable': True,
    'auto_install': False,
}
