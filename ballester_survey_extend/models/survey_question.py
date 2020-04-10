# -*- coding: utf-8 -*-
# Odoo, Open Source Ballester Survey Extend.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#
 
from odoo import fields, models, api, _
    
# new fields 
class SurveyQuestion(models.Model):
    _inherit = 'survey.question'
     
    question_type = fields.Selection([('entry', 'Entry'), ('exit', 'Exit')], string='Question Type')