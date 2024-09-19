{
    'name': 'YBO POS Access Right',
    'summary': 'To Restrict POS features for cashiers',
    'description': """This app allows you to enable or disable POS features depending on the access rights granted to the cashiers""",
    'version': '1.0',
    'website': "https://www.ybo-services.com",
    'author': "YBO Services",
    'maintainer': 'YBO Services',
    'depends': ['pos_hr'],
    'data': [
        'views/hr_employee_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'ybo_pos_access_right/static/src/js/PosStore.js',
            'ybo_pos_access_right/static/src/js/refund_button.js',
            'ybo_pos_access_right/static/src/js/ActionpadWidget.js',
            'ybo_pos_access_right/static/src/js/ProductScreen.js',
            'ybo_pos_access_right/static/src/xml/ActionpadWidget.xml'
            'ybo_pos_access_right/static/src/xml/refund_button.xml'
        ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
