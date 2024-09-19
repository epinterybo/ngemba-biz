# -*- coding: utf-8 -*-
{
    'name': "CW Bonus System",

    'summary': "CW Bonus System for Employeee",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'hr', 'contacts', 'stock', 'point_of_sale'],
    'application': True,
    'license': "LGPL-3",

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/cw_period_tracking_view.xml',
        'views/cw_employee_bonus_view.xml',
        'views/cw_periodical_prize_view.xml',
        'views/cw_winner_prize_view.xml',
        'views/cw_periodical_point_view.xml',
        'views/cw_points_tracking_view.xml',
        'views/product_template_views.xml',
        'views/product_category_views.xml',
        'views/sale_order_form_view.xml',
        'views/pos_order_view.xml',
        'views/menu_items.xml',
        'data/service_cron.xml',
        'views/cw_front_start_bonus.xml',
    ],
    
    'assets': {
        'web.assets_backend': [
            'cw_bonus_system/static/src/css/style.scss',
        ],
        
        'point_of_sale._assets_pos': [
            'cw_bonus_system/static/src/js/Screens/ProductScreen/ControlButtons/BonusReferralButton.js',
            'cw_bonus_system/static/src/js/Screens/BonusEmployeeLine/BonusEmployeeLine.js',
            'cw_bonus_system/static/src/js/Screens/BonusEmployee.js',
            'cw_bonus_system/static/src/js/store/model.js',
            'cw_bonus_system/static/src/js/store/bonus_employee_store.js',
            'cw_bonus_system/static/src/js/store/event_bus.js',
            #'cw_bonus_system/static/src/xml/Screens/ProductScreen/ControlButtons/BonusReferralbutton.xml',
            'cw_bonus_system/static/src/xml/**/*',
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

