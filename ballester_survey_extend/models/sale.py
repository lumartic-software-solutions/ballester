# -*- coding: utf-8 -*-
# Odoo, Open Source Ballester Product.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('check_compliance', 'Compliance Checked'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    survey_input_ids= fields.One2many('survey.user_input','sale_order_id','Answer')
    survey_input_count = fields.Integer(compute='_compute_survey', string='Receptions', default=0, store=True, compute_sudo=True)

    @api.depends('survey_input_ids')
    def _compute_survey(self):
        for order in self:
            order.survey_input_count = len(order.survey_input_ids)
    
    @api.multi
    def action_view_survey_input(self):
        '''
        This function returns an action that display existing survey input  of given purchase order ids.
        When only one found, show the survey input immediately.
        '''
        
        action = self.env.ref('survey.action_survey_user_input')
        result = action.read()[0]

        result['context'] = {'default_sale_order_id': self.id,'default_search_sale_order_id':self.id}
        survey_input_ids = self.mapped('survey_input_ids')
        #choose the view_mode accordingly
        if not survey_input_ids or len(survey_input_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (survey_input_ids.ids)
        elif len(survey_input_ids) == 1:
            res = self.env.ref('survey.survey_user_input_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = survey_input_ids.id
        return result
    
    
    @api.multi
    def check_compliance(self):
        survey_sddr = False
        survey_waste = False
        survey_new = False
        survey_recycled = False
        survey_obj = self.env['survey.survey']
        if self.sales_type:
            if self.sales_type == 'new' :
                survey_new = self.env['ir.config_parameter'].sudo().get_param('new_compliance_id')   
            elif self.sales_type == 'recycled':
                survey_recycled = self.env['ir.config_parameter'].sudo().get_param('recycled_compliance_id')	
            elif self.sales_type == 'sddr':
                survey_sddr = self.env['ir.config_parameter'].sudo().get_param('sddr_compliance_id')
            elif self.sales_type == 'waste':
                survey_waste = self.env['ir.config_parameter'].sudo().get_param('waste_compliance_id') 
        if survey_new:
            survey_new_id = survey_obj.search([('id', '=', survey_new)])
            return {
                'type': 'ir.actions.act_url',
                'name': "Results of the Survey",
                'target': 'self',
                'res_id': self.id,
                'url': survey_new_id.with_context(relative_url=True, sale=True).public_url + "/" + str(self.id)
                }


        if survey_recycled:
            survey_recycled_id = survey_obj.search([('id', '=', survey_recycled)])
            return {
                'type': 'ir.actions.act_url',
                'name': "Results of the Survey",
                'target': 'self',
                'res_id': self.id,
                'url': survey_recycled_id.with_context(relative_url=True, sale=True).public_url + "/" + str(self.id)
                }


        if survey_sddr:
            survey_sddr_id = survey_obj.search([('id', '=', survey_sddr)])
            return {
                'type': 'ir.actions.act_url',
                'name': "Results of the Survey",
                'target': 'self',
                'res_id': self.id,
                'url': survey_sddr_id.with_context(relative_url=True, sale=True).public_url + "/" + str(self.id)
                }

        if survey_waste:
            survey_waste_id = survey_obj.search([('id', '=', survey_waste)])

            return {
                'type': 'ir.actions.act_url',
                'name': "Results of the Survey",
                'target': 'self',
                'res_id': self.id,
                'url': survey_waste_id.with_context(relative_url=True, sale=True).public_url + "/" + str(self.id)
            }
