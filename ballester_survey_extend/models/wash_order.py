# -*- coding: utf-8 -*-
# Odoo, Open Source Ballester Product.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class WashOrder(models.Model):
    _inherit = 'wash.order'


    '''@api.depends('survey_input_ids')
    def _compute_survey(self):
        for order in self:
            order.survey_input_count = len(order.survey_input_ids)
    
    @api.multi
    def action_view_survey_input(self):
        
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
        return result'''
    

    @api.depends('survey_input_ids')
    def _compute_survey(self):
        for order in self:
            order.survey_input_count = len(order.survey_input_ids)

    survey_input_ids= fields.One2many('survey.user_input','wash_order_id','Answer')
    survey_input_count = fields.Integer(compute='_compute_survey', string='Receptions', default=0, store=True, compute_sudo=True)    
	

    @api.multi
    def action_view_survey_input(self):
        '''
        This function returns an action that display existing survey input  of given purchase order ids.
        When only one found, show the survey input immediately.
        '''
        
        action = self.env.ref('survey.action_survey_user_input')
        result = action.read()[0]

        result['context'] = {'default_wash_order_id': self.id,'default_search_wash_order_id':self.id}
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
        survey_container = False
        survey_drum = False
        survey_crush = False
        survey_compact = False
        survey_obj = self.env['survey.survey']
        if self.type_of_order:
            if self.type_of_order == 'container' :
                survey_container = self.env['ir.config_parameter'].sudo().get_param('container_compliance_id') 	
            elif self.type_of_order == 'drum':
                survey_drum = self.env['ir.config_parameter'].sudo().get_param('drum_compliance_id')
            elif self.type_of_order == 'crush':
                survey_crush = self.env['ir.config_parameter'].sudo().get_param('crush_compliance_id') 
            elif self.type_of_order == 'compact':
                survey_compact = self.env['ir.config_parameter'].sudo().get_param('compact_compliance_id') 
        if survey_container:
            survey_container_id = survey_obj.search([('id', '=', survey_container)])
            if survey_container_id:
                return {
                'type': 'ir.actions.act_url',
                'name': "Results of the Survey",
                'target': 'self',
                'res_id': self.id,
                'url': survey_container_id.with_context(relative_url=True, wash=True).public_url + "/" + str(self.id)
                }

        if survey_drum:
            survey_drum_id = survey_obj.search([('id', '=', survey_drum)])
            if survey_drum_id:
                return {
		        'type': 'ir.actions.act_url',
		        'name': "Results of the Survey",
		        'target': 'self',
		        'res_id': self.id,
		        'url': survey_drum_id.with_context(relative_url=True, drum=True).public_url + "/" + str(self.id)
		    }
        if survey_crush:
            survey_crush_id = survey_obj.search([('id', '=', survey_crush)])
            if survey_crush_id:
                return {
                'type': 'ir.actions.act_url',
                'name': "Results of the Survey",
                'target': 'self',
                'res_id': self.id,
                'url': survey_crush_id.with_context(relative_url=True, crush=True).public_url + "/" + str(self.id)
                }
        if survey_compact:
            survey_compact_id = survey_obj.search([('id', '=', survey_compact)])
            if survey_compact_id:
                return {
                'type': 'ir.actions.act_url',
                'name': "Results of the Survey",
                'target': 'self',
                'res_id': self.id,
                'url': survey_compact_id.with_context(relative_url=True, compact=True).public_url + "/" + str(self.id)
                }
