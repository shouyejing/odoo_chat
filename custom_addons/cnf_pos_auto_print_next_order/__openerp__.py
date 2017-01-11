#!/usr/bin/python
# -*- encoding: utf-8 -*-
# author: minhld

{
    'name': "Canifa POS auto print next order",

    'summary': """
        Point Of Sale
        """,

    'description': """
        Auto click button print and next order on pos screen
        This module is based on Point of Sale Module.
    """,

    'author': "Canifa",
    'website': "http://canifa.com",
    'category': 'Point Of Sale',
    'version': '1.0',

    # any module necessary for this one to work correctly

    'depends': ['point_of_sale', 'product'],
    # always loaded
    'data': [
        'views/cnf_pos.xml',
    ],
    'application': True,
    'qweb': ['static/src/xml/cnf_pos.xml',
             ],
    # only loaded in demonstration mode
}
