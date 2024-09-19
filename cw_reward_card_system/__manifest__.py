# -*- coding: utf-8 -*-
{
    'name': "CW Reward Card System",

    'summary': "CW Reward Card System as required by Computer and working with Quote and POS",

    'description': """
CW Reward Card System as required by Computer and working with Quote and POS - We can make this a little bit longer
    """,

    'author': "Computer World",
    'website': "https://www.cw.vu",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'point_of_sale', 'account'],
    'installable': True,
    'application': True,
    'license': "LGPL-3",

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/product_template_views.xml',
        'views/cw_reward_card_views.xml',
        'views/cw_reward_card_wizard_views.xml',
        'views/sale_order_views.xml',
        'views/menu_items.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    
    'assets': {
        'point_of_sale._assets_pos': [
            'cw_reward_card_system/static/src/**/*',
        ],
    },
}

