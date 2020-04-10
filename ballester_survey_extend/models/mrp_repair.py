# -*- coding: utf-8 -*-
# Odoo, Open Source Ballester Product.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class MrpRepair(models.Model):
    _inherit = 'mrp.repair'


    @api.depends('survey_input_ids')
    def _compute_survey(self):
        for order in self:
            order.survey_input_count = len(order.survey_input_ids)

    survey_input_ids= fields.One2many('survey.user_input','repair_id','Answer')
    survey_input_count = fields.Integer(compute='_compute_survey', string='Receptions', default=0, store=True, compute_sudo=True)    
	

    @api.multi
    def action_view_survey_input(self):
        '''
        This function returns an action that display existing survey input  of given purchase order ids.
        When only one found, show the survey input immediately.
        '''
        
        action = self.env.ref('survey.action_survey_user_input')
        result = action.read()[0]

        result['context'] = {'default_repair_id': self.id,'default_search_repair_id':self.id}
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
        repair_container = False
        survey_obj = self.env['survey.survey']
        repair_container = self.env['ir.config_parameter'].sudo().get_param('repair_compliance_id') 
        if repair_container:
            repair_container_id = survey_obj.search([('id', '=', repair_container)])
            if repair_container_id:
                return {
                'type': 'ir.actions.act_url',
                'name': "Results of the Survey",
                'target': 'self',
                'res_id': self.id,
                'url': repair_container_id.with_context(relative_url=True, repair=True).public_url + "/" + str(self.id)
                }

