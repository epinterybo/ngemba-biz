# -*- coding: utf-8 -*-
{
    'name': "CW Taking Pictures By Events",

    'summary': "CW Taking Pictures By Events on every events which should be done",

    'description': """
CW Taking Pictures By Events on every events which should be done - This is related to POS and Stock Picking as those are the 2 place where Images should be taken
    """,

    'author': "Computer World",
    'website': "https://www.cw.vu",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'point_of_sale', 'stock'],
    
    'installable': True,
    'application': True,
    'post_init_hook': 'post_init_hook',

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/pos_order_view.xml',
        'views/stock_picking_view.xml',
        #'views/cw_taken_picture_details_views.xml',
        'views/cw_taking_positions_cameras_view.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/menu_items.xml',
        'data/service_cron.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'cw_taking_pictures_by_events/static/src/css/custom_styles.css',
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

