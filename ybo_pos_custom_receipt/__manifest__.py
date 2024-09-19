{
    'name': 'YBO POS Custom Receipt',
    'summary': 'This module hide the text "Odoo 17 Point of Sale" on the Odoo 17 POS receipt',
    'version': '1.0',
    'author': "YBO Services",
    'maintainer': 'YBO Services',
    'website': "https://www.ybo-services.com",
    'depends': ['base', 'sale', 'point_of_sale'],
    'data': [
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'ybo_pos_custom_receipt/static/src/js/*.js',
            'ybo_pos_custom_receipt/static/src/xml/*.xml',
        ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
