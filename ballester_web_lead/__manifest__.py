#  -*- coding: utf-8 -*-
#  Odoo, Open Source Ballester Web Lead.
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). 
{
    'name': 'Ballester Web Lead',
    'category': 'sale',
    'author': 'ITMusketeers Consultancy Services LLP',
    'description': """
================================================================================

1.  Ballester Sale.
2.  Web CRM

================================================================================
""",
    'depends': [ 'base', 'web','sale_management','website_crm'],
    'summary': 'Ballester Sale.',

    'data': [ 
             'data/lead_sequence_data.xml',
            'views/crm_view.xml',
            'views/website_crm_view.xml',
            ],
    'qweb': [
        
    ],

    'installable': True,

}
