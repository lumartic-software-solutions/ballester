# -*- coding: utf-8 -*-
# Odoo, Open Source Ballester Inventory.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Ballester Inventory',
    'category': 'Stock',
    'author': 'ITMusketeers Consultancy Services LLP',
    'description': """
================================================================================

1.Customization in Inventory .

================================================================================
""",
    'depends': ['base', 'web', 'sale', 'product',  'purchase', 'stock'],
    'summary': 'Customization in Inventory ',

    'data': [ 
           # 'data/serial_sequence_data.xml',
            'views/ballester_stock_picking_view.xml',
            ],
  

    'installable': True,

}
