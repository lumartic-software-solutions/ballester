# -*- coding: utf-8 -*-
# Odoo, Open Source Ballester Survey Extend.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).# 

from odoo import fields, models
    
# new fields 
class HrJob(models.Model):
    _inherit = 'hr.job'
    
    survey_id = fields.Many2one(
        'survey.survey', "Incidents Form",
        help="Choose an interview form for this job position and you will be able to print/answer this interview from all applicants who apply for this job")
