{
    'name': 'YBO POS Surcharge Price',
    'summary': 'This module provides functionality to apply extra fees or surcharges to items or services processed through the POS system',
    'description': """
The "YBO POS Surcharge Price" module is designed to integrate with Odoo's Point of Sale (POS) system to handle additional surcharges on prices. It provides functionality to apply extra fees or surcharges to items or services processed through the POS system. This can be particularly useful for businesses that need to pass on additional costs to customers, such as service charges, environmental fees, or any other type of surcharge
""",
    'version': '1.0',
    'category': 'Point of Sale',
    'author': "YBO Services",
    'maintainer': 'YBO Services',
    'website': "https://www.ybo-services.com",
    'depends': ['point_of_sale'],
    'data': [
        'views/res_config_settings_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'ybo_pos_surcharge/static/src/js/*.js',
            'ybo_pos_surcharge/static/src/xml/*.xml',
        ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
