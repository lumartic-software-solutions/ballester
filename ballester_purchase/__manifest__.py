# -*- coding: utf-8 -*-
# Odoo, Open Source Ballester Sales.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Ballester Purchase',
    'category': 'Purchase',
    'author': 'Divya Vyas',
    'description': """
================================================================================

1.Customization in Purchase and Purchase Reports.

================================================================================
""",
    'depends': ['base', 'web', 'purchase', 'product', 'stock', 'survey', 'fleet', 'ballester_partner'],
    'summary': 'Customization in Purchase and Purchase Reports.',
    'data': [ 
            'views/asset.xml',
            'report/delivery_note_purchase_report.xml',
            'report/waste_certificate.xml',
            'report/waste report.xml',
            'report/inherit_purchase_report.xml',
            'report/consignment_note_report.xml',
            'wizard/quantity_unreserved_view.xml',
            'wizard/purchase_action_wizard.xml',
	    #'wizard/barcode_wizard_view.xml',
            'views/ballester_purchase_report.xml',
            'views/custom_ballester.xml',
            'views/purchase_inherit_view.xml',
            'views/sequence_view.xml',
            "views/partner_view.xml"
            ],
  
    'installable': True,

}
