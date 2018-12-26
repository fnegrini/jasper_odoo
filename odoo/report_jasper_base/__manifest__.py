# -*- coding: utf-8 -*-
{
    'name': "Jasper Reports for Odoo",

    'summary': """
        Jasper Reports for Odoo (no jasper server needed)
    """,

    'description': """
        Jasper Reports integration without the need to create and manage a jasper server
    """,

    'author': "Artios",
    'website': "http://www.artios.com.br",
    'category': 'Technical Settings',
    'version': '0.1',

    'depends': ['base'],

    'data': [
       # 'security/ir.model.access.csv',
        'data/jasper_data.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
