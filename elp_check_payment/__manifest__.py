{
    'name': 'Check invoice payement',
    'version': '1.0',
    'description': 'Cehck invoice paiement',
    'summary': 'Check invoice payement',
    'author': 'ELPERF & Thomas ATCHA',
    'website': 'https://elperf.com',
    'license': 'LGPL-3',
    'category': 'Tools',
    'depends': [
        'base','stock','account','sale_management','sale'
    ],
    'data': [
        'views/stock_view.xml',
        'data/data.xml',
    ],
    'demo': [
        
    ],
    'auto_install': False,
    'application': False,
    'assets': {
        
    }
}