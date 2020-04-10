# -*- coding: utf-8 -*-
# Odoo, Open Source Ballester Survey Extend.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#

from odoo import fields, models,api,_
    
# new fields 
class HrEmployee(models.Model):
    _inherit = 'hr.employee'
     
    incidents_count = fields.Integer(
        string='Number of Incidents',
        readonly=True, compute='_compute_incidents_count')
    incidents_manager_id = fields.Many2one('hr.employee',string='Incidents Reporting Manager',required=True)
    controler = fields.Boolean('Controler')
    
    # compute total no of incidents 
    @api.one
    def _compute_incidents_count(self):
        self.incidents_count = self.env['survey.user_input_line'].search_count([('employee_id', '=', self.id),('execution_type','=','send_mail')])
    
    # details of incidents report using smart button in employee
    @api.multi      
    def incidents_report_details(self):
        action = self.env.ref('ballester_survey_extend.action_survey_user_input_line_extend').read()[0]
        action['context'] = {
            'search_default_employee_id': self.id,
            'search_default_execution_type': 'send_mail',
        }
        return action
