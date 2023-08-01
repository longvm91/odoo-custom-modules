# -*- coding: utf-8 -*-
{
    'name': "Aged Inventory Report",

    'summary': """
        Aged Inventory Report 1-30,31-90,91-180,181-360,360+""",

    'description': """
        
    """,
    "license": "LGPL-3",
    'author': "Jason Vu",
    'website': "https://github.com/longvm91/odoo-custom-modules/tree/16.0/aged_inventory_report",
    'email': "longvm91@gmail.com",
    'category': 'Warehouse',
    'version': '16.0.1.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'stock_account', 'product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'reports/aged_inventory_report_views.xml',
    ],
    # 'images': ['static/img/report1.png', 'static/img/report2.png'],
    "assets": {
        # "web.assets_backend": [
        #     "imex_inventory_report/static/src/css/**/*",
        #     "imex_inventory_report/static/src/js/**/*",
        # ],
    },
    "installable": True,
}
