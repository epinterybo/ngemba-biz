# -*- coding: utf-8 -*-
{
    'name': "CW Costing App",

    'summary': "To calculate costing of each product after shipping and duties",

    'description': """
Long description of module's purpose
    """,

    'author': "CW.VU",
    'website': "https://www.cw.vu",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'stock'],
    'application': True,
    'license': "LGPL-3",

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/cw_monthly_exchange_rate_view.xml',
        'views/cw_costing_grouping_view.xml',
        'views/product_category_view.xml',
        'views/cw_costing_unique_product_view.xml',
        'views/cw_harmmonized_code_view.xml',
        'views/purchase_view.xml',
        'views/menu_items.xml',
        'views/product_template_view.xml',
        'data/service_cron.xml',
    ],
    
    'assets': {
        'web.assets_backend': [
            'cw_costing/static/src/scss/styles.scss',
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

