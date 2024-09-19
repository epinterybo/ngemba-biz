# -*- coding: utf-8 -*-
{
    'name': "RPC XML Debug Test",

    'summary': "RPC XML Debug Test",

    'description': """
RPC XML Debug Test - RPC XML Debug Test - RPC XML Debug Test - RPC XML Debug Test
    """,

    'author': "Fotechys",
    'website': "https://www.sdkgames.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'installable': True,
    'application': True,
    'license': "LGPL-3",

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

