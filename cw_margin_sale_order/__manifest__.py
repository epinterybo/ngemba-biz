# -*- coding: utf-8 -*-
{
    'name': "CW Margin Sale Order",

    'summary': "Set selling price based on margin percentage",

    'description': """
This module allows setting the selling price of a product in a sale order by specifying the margin percentage.
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'product'],
    'installable': True,
    'application': False,
    'license': "LGPL-3",

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/sale_order_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

