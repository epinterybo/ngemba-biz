{
    'name': 'CW POS International Card Button',
    'summary': 'Add an INT button for international card payments in POS',
    'version': '1.0',
    'category': 'Point of Sale',
    'author': "CW.VU",
    'maintainer': 'YBO Services',
    'website': "https://www.cw.vu",
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_config_view.xml',
        'views/res_config_settings_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'cw_pos_international_card_button/static/src/js/*.js',
            'cw_pos_international_card_button/static/src/xml/*.xml',
            # 'cw_pos_international_card_button/static/src/css/*.scss',
        ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
