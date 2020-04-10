# -*- coding: utf-8 -*-
# Odoo, Open Source Ballester Survey Extend.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).# 

from odoo import fields, models,api,_
from odoo.exceptions import UserError
    
# new fields 
class SurveyUserInputLine(models.Model):
    _name = 'survey.user_input_line'
    _inherit = ['mail.thread','mail.activity.mixin','survey.user_input_line']
     
    comment = fields.Text(string='Comment')
    state = fields.Selection([('draft', 'Draft'), ('mail_send', 'Mail Send'), ('in_progress', 'In Progress'), ('closed', 'Closed'),('permanent','Permanent')],default='draft', string='State')
    execution_type = fields.Selection([('continue', 'Continue'), ('send_mail', 'Send Mail')], string='Execution Type',related='value_suggested.execution_type')
    question_type = fields.Selection([('entry', 'Entry'), ('exit', 'Exit')], string='Question Type',related='question_id.question_type')
    employee_id = fields.Many2one('hr.employee',string='Employee',related='user_input_id.employee_id')
    incidents_manager_id = fields.Many2one('hr.employee',string='Incidents Reporting Manager',related='user_input_id.employee_id.incidents_manager_id')
    get_incidents_url = fields.Text(compute="_get_incidents_url",string="Incidents URL",store=False)
    get_incidents_manager_email = fields.Text(compute='_get_incidents_manager_email',string="get incidents manager email", store=False)
    get_controller_email = fields.Text(compute='_get_controller_email',string="get Controller email", store=False)

    # set state into in progress
    @api.multi
    def action_in_progress(self):
        for rec in self:
            rec.write({'state': 'in_progress'})
    
    # set state into in closed
    @api.multi
    def action_closed(self):
        for rec in self:
            rec.write({'state': 'closed'})
            
    # set state into in permanent        
    @api.multi
    def action_permanent(self):
        for rec in self:
            rec.write({'state': 'permanent'})
    
    # set incidents manager email          
    @api.multi
    def _get_incidents_manager_email(self):
        for rec in self:
            if rec.employee_id.incidents_manager_id :
                emails = ''
                employee_ids = self.env['hr.employee'].browse(rec.employee_id.incidents_manager_id.id)
                for employee in employee_ids:
                    if employee.work_email:
                        emails += employee.work_email
                        emails += ','
                    elif employee.user_id :
                        if employee.user_id.partner_id.email :
                            emails += employee.user_id.partner_id.email
                            emails += ','
                rec.get_incidents_manager_email = emails[:-1]
            else:
                raise UserError(_('No Found Incidents Reporting Manager For %s Employee !') %rec.employee_id.name)
    @api.multi
    def _get_controller_email(self):
        for rec in self:
            if rec.value_suggested:
                if rec.value_suggested.controller_id:
                    rec.get_controller_email  = rec.value_suggested.controller_id.work_email or rec.value_suggested.controller_id.user_id.partner_id.email or ''
    
    # get incidents url      
    @api.multi
    def _get_incidents_url(self):
        for rec in self:
            base_url = self.env['ir.config_parameter'].get_param(
                'web.base.url',
                default='http://localhost:8090'
            )
            rec.get_incidents_url = (
                '{}/web#db={}&id={}&view_type=form&'
                'model=survey.user_input_line').format(
                    base_url,
                    self.env.cr.dbname,
                    rec.id
                )
