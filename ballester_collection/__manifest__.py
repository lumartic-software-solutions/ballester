{
    'name': 'Ballester Collection',
    'category': 'Collection',
    'author': 'Divya Vyas',
    'description': """
================================================================================
Collection Order
================================================================================
""",
    'depends': ['base', 'ballester_purchase', 'ballester_sale'],

    'data': [
        'report/report_bill_of_lading.xml',
	 'views/report.xml',
        'data/mail_template_data.xml',
        'data/ir_sequence_data.xml',
        'views/bill_of_lading.xml',
        'views/collection_order_view.xml',
        'views/purchase_view.xml',
        'views/sale_view.xml',
	'views/invoice_view.xml',
        'views/collection_report_view.xml',
       
    ],

    'installable': True,

}
