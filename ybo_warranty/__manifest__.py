{
    'name': 'YBO Warranty Management',
    'summary': 'This module leveraging product categories and variants for flexible and efficient warranty management',
    'version': '1.0',
    'author': "YBO Services",
    'maintainer': 'YBO Services',
    'website': "https://www.ybo-services.com",
    'depends': ['base', 'web', 'product', 'sale', 'sale_management', 'sale_product_configurator', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'data/seq_product_warranty.xml',
        'views/product_template_views.xml',
        'views/product_category_view.xml',
        'views/sale_order_views.xml',
        'views/warranty_views.xml',
    ],
    'assets': {'web.assets_backend': [
        'ybo_warranty/static/src/js/product_configurator_dialog/product_configurator_dialog.js',
    ], },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
