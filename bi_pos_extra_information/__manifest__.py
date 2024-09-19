# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': "Add POS Extra Fields | Add Extra Custom Fields on POS",
    'version': '17.0.0.0',
    'category': 'Point of Sale',
    'summary': "pos extra information receipt pos extra field info point of sale extra custom field information pos order extra information pos extra fields info point of sale extra information pos custom field in pos information extra information point of sale receipt",
    'description': """Point of Sale Extra Information Odoo app allows businesses to collect and display additional information related to products, services, or promotions during the checkout process, providing customers with valuable insights, Added extra information also added to point of sale order, User can enable or disable this feature as per need.""",
    'author': 'BrowseInfo',
    'website': "https://www.browseinfo.com",
    'price': 20,
    'currency': 'EUR',
    'depends': ['base', 'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_setting.xml',
        'views/pos_extra_info.xml',
        'views/pos_order.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'bi_pos_extra_information/static/src/js/models.js',
            'bi_pos_extra_information/static/src/js/posStore.js',
            'bi_pos_extra_information/static/src/js/Screens/ProductScreen/ControlButtons/ExtraInfoButton.js',
            'bi_pos_extra_information/static/src/js/Popups/ExtraInfoPopup.js',
            'bi_pos_extra_information/static/src/xml/**/*',
        ],
    },
    'license': 'OPL-1',
    'installable': True,
    'application': False,
    'auto_install': False,
    'live_test_url':'https://youtu.be/lT95-yIrVIo',
    "images":['static/description/POS-Extra-Information.gif'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
