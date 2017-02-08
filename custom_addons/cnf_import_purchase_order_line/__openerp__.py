# -*- coding: utf-8 -*-


{
    "name": "Import Purchase order line Using Excel",
    "version": "1.0",
    "depends": ['base','purchase'],
    "author": "Canifa.com",
    "category": "Custom",
    "description": """
    This Module can be used to import the XLS to the purchase orders line object
    
    """,
    "init_xml": [],
    "data": [
        'wizard/wiz_purchase.xml',
        # 'views/purchase_inherit.xml',
    ],
    'depends': ['purchase'],
    'demo_xml': [],
    'js':[],
    'qweb':[],
    'css':[],
    'img':[''],
    'installable': True,
    'auto_install': False,
    'application': True,
#    'certificate': 'certificate',
}
