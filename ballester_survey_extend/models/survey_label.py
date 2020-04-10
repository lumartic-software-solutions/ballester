# -*- coding: utf-8 -*-
# Odoo, Open Source Ballester Survey Extend.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).# 

from odoo import fields, models
    
# new fields 
class SurveyLabel(models.Model):
    _inherit = 'survey.label'
     
    execution_type = fields.Selection([('continue', 'Continue Qustion'), ('send_mail', 'Send Mail Controler')], string='Execution Type')
    controller_id = fields.Many2one('hr.employee','Controler')
    page_question_id = fields.Many2one('survey.page','Select Page')
    
