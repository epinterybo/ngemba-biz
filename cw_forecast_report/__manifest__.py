# -*- coding: utf-8 -*-
{
    'name': "CW OCM Forecast Report",

    'summary': "CW OCM Forecast Report useful to define ordering rule",

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
    'depends': ['base', 'sale', 'purchase', 'stock', 'contacts', 'point_of_sale'],
    'application': True,
    'license': "LGPL-3",

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/forecast_reporting_view.xml',
        'views/res_partner_views.xml',
        'views/cw_order_line_view.xml',
        'views/cw_po_order_line_view.xml',
        'views/cw_purchase_order_view.xml',
        'views/cw_product_delivery_view.xml',
        'views/cw_stock_take_view.xml',
        'views/product_template_views.xml',
        'views/cw_sale_invoice_view.xml',
        'views/cw_partner_view.xml',
        'views/menu_items.xml',
        'views/views.xml',
        'views/templates.xml',
        'data/service_cron.xml',
        'views/forecast_report_legend.xml',
    ],
    
    
    'assets': {
        'web.assets_backend': [
            'cw_forecast_report/static/src/views/forecast_report_legend.js',
            'cw_forecast_report/static/src/views/forecast_report_legend_listview.js',
            'cw_forecast_report/static/src/views/forecast_report_legend.xml',
            'cw_forecast_report/static/src/views/forecast_report_legend_listview.xml',
            'cw_forecast_report/static/src/css/custom_styles.css',
            'cw_forecast_report/static/src/js/handle_buttons.js',
            'cw_forecast_report/static/src/xml/handle_buttons.xml',
            #'cw_forecast_report/static/src/js/copy_button.js',
        ],
#        'web.assets_frontend': [
#           #'purchase/static/src/js/purchase_datetimepicker.js',
#           #'purchase/static/src/js/purchase_portal_sidebar.js',
#       ],
    },
    
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

