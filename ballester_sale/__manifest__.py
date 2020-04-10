# -*- coding: utf-8 -*-
# Odoo, Open Source Ballester Sales.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Ballester Sales',
    'category': 'Sales',
    'author': 'Divya Vyas',
    'description': """
================================================================================

1.Customization in Sales .

================================================================================
""",
    'depends': ['base', 'web', 'sale', 'product', 'stock', 'website','account','website_quote'],
    'summary': 'Customization in Sales ',
    'data': [
            'views/asset.xml',
		
            'report/delivery_note_sale_report.xml',
            'report/container_cleaning_certificates_report.xml',
            'report/container_washing_certificates_report.xml',
	'report/inherit_customer_invoice.xml',
            'report/drum_certificates_sddr_report.xml',
            'report/consignment_note_report.xml',
            'report/inherit_sale_report.xml',
            'views/ballester_sale_report.xml',
		'views/stock_move.xml',
        #             'views/custom_report_layout.xml',
            'views/sale_inherit_view.xml',
            'views/sequence_view.xml',
    ],

    'installable': True,

}
