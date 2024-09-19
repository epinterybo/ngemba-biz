{
    'name': 'CW POS Custom Receipt',
    'description': """
Add certain customization to the Odoo 17 POS receipt
""",
    'version': '1.0',
    'author': "CW.VU",
    'maintainer': 'YBO Services',
    'website': "https://www.cw.vu",
    'depends': ['base', 'sale', 'point_of_sale'],
    'data': [
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'cw_pos_custom_receipt/static/src/css/*.css',
            'cw_pos_custom_receipt/static/src/js/*.js',
            'cw_pos_custom_receipt/static/src/xml/*.xml',
        ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
