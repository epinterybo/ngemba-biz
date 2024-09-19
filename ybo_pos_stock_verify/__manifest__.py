{
    'name': 'YBO POS Stock Verify',
    'description': """
A module that adds a 2 step stock verification step to the Odoo 17 POS orders
""",
    'version': '1.0',
    'author': "CW.VU",
    'maintainer': 'YBO Services',
    'website': "https://www.cw.vu",
    'depends': ['stock', 'sale', 'point_of_sale'],
    'data': [
        'data/dummy_client_data.xml',
        'views/res_config_settings_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'ybo_pos_stock_verify/static/src/js/*.js',
        ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
