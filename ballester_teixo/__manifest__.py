{
    'name': 'Teixo Integration',
    'category': 'Integration',
    'author': 'Bhavik Vyas',
    'website': 'www.odoowikia.com',
    'description': """
================================================================================
Integration Of Teixo With Odoo.
================================================================================
""",
    'depends': ['base', 'ballester_product', 'sale', 'purchase', 'stock', 'ballester_survey_extend', 'contacts', 'ballester_collection', 'ballester_sale', 'ballester_purchase'],
    'summary': 'Integration Of Teixo With Odoo.',

    'data': [
              'wizard/change_di_state_wizard.xml',
              'views/teixo_view.xml',
              'views/res_config_settings_views.xml',
              'views/sale_teixo_view.xml',
              'views/partner_teixo_view.xml',
              'views/center_view.xml',
              'views/purchase_teixo_view.xml',
              'views/ collection_teixo_view.xml',
	      'views/invoice_teixo_view .xml',
              'views/operation_teixo_view.xml',
              'views/waybill_report.xml',
              'security/ir.model.access.csv',
              'data/center_sequence_data.xml'
    ],

    'installable': True,

}
