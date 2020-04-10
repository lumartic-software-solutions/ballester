#  -*- coding: utf-8 -*-
#  Odoo, Open Source Ballester Survey Extend.
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl
{
    'name': 'Ballester Survey Extend',
    'category': 'Survey',
    'author': 'ITMusketeers Consultancy Services LLP',
    'description': """
================================================================================

1.  Customization in Survey.

================================================================================
""",
    'depends': ['mail', 'website', 'hr', 'base', 'web', 'survey','sale','purchase', 'hr_recruitment_survey','ballester_sale','ballester_purchase','ballester_wash','mrp_repair'],
    'summary': 'Customization in Survey.',

    'data': [ 
            'security/ir.model.access.csv',
            'data/incidents_mail_template.xml',
            'views/employee_view.xml',
            'views/survey_view.xml',
            'views/survey_page_view.xml',
            'views/survey_user_input_view.xml',
            'views/sale_view.xml',
            'views/purchase_view.xml',
            'views/survey_question_view.xml',
            'views/survey_user_input_line_view.xml',
            'views/website_login_view.xml',
            'views/incidents_report_view.xml',
	    'views/mrp_repair_view.xml',
	    'views/wash_view.xml',
            'views/res_config_settings_purchase_views.xml',
            'views/res_config_settings_sale_views.xml',
		'views/res_config_settings_repair_view.xml',
	'views/res_config_settings_wash_view.xml',
            ],
    'installable': True,
}
