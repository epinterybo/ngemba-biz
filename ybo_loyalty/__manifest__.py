{
    'name': 'YBO Loyalty Extension',
    'summary': 'Extends loyalty program functionality',
    'version': '1.0',
    'author': "YBO Services",
    'maintainer': 'YBO Services',
    'website': "https://www.ybo-services.com",
    'depends': ['base', 'product', 'loyalty', 'point_of_sale', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/loyalty_card_views.xml',
        'views/loyalty_reward_views.xml',

    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}
