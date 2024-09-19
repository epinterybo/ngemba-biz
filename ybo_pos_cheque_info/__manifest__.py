{
    'name': 'YBO POS Cheque Info',
    'description': """
The objective is to enhance the Odoo 17 POS check payment method by adding a cheque information pop-up, enforcing required fields completion, and ensuring check information availability on the order detail page.
""",
    'summary': 'The module adds a cheque information pop-up for cheque payment methods on the Odoo 17 POS',
    'version': '1.0',
    'author': "YBO Services",
    'maintainer': 'YBO Services',
    'website': "https://www.ybo-services.com",
    'depends': ['base', 'sale', 'point_of_sale'],
    'data': [
        'views/pos_config_view.xml',
        'views/pos_payment_method_view.xml',
        'views/pos_order_view.xml',
        'views/account_journal_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'ybo_pos_cheque_info/static/src/css/*.css',
            'ybo_pos_cheque_info/static/src/js/*.js',
            'ybo_pos_cheque_info/static/src/xml/*.xml',
        ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
