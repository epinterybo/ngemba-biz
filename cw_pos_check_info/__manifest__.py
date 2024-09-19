{
    'name': 'CW POS Check Info',
    'description': """
The objective is to enhance the Odoo 17 POS check payment method by automating the check information pop-up, enforcing required fields completion, removing the customer field, and ensuring check information availability during bank reconciliation.""",
    'version': '1.0',
    'author': "CW.VU",
    'maintainer': 'YBO Services',
    'website': "https://www.cw.vu",
    'depends': ['base', 'sale', 'point_of_sale'],
    'data': [
        'views/pos_config_view.xml',
        'views/pos_payment_method_view.xml',
        'views/pos_order_view.xml',
        'views/account_journal_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'cw_pos_check_info/static/src/css/*.css',
            'cw_pos_check_info/static/src/js/*.js',
            'cw_pos_check_info/static/src/xml/*.xml',
        ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
