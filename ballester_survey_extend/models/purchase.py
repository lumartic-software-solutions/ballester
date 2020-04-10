# -*- coding: utf-8 -*-
# Odoo, Open Source Ballester Product.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api, _


class Purchaseorder(models.Model):
    _inherit = 'purchase.order'
    
    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
    ('check_compliance', 'Compliance Checked'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
        ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    survey_input_ids= fields.One2many('survey.user_input','purchase_order_id','Answer')
    survey_input_count = fields.Integer(compute='_compute_survey', string='Receptions', default=0, store=True, compute_sudo=True)
    user_id = fields.Many2one('res.users','Assign To', default=lambda self: self.env.user , store=True)

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

        result['context'] = {'default_purchase_order_id': self.id,'default_search_purchase_order_id':self.id}
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
        survey_complex = False
        survey_minor = False
        survey_obj = self.env['survey.survey']
        if self.purchase_type:
            if self.purchase_type == 'complex':
                survey_complex = self.env['ir.config_parameter'].sudo().get_param('complex_purchase_id')
            if self.purchase_type == 'minor':
                survey_minor = self.env['ir.config_parameter'].sudo().get_param('minor_purchase_id')
        if survey_complex:
            survey_complex_id = survey_obj.search([('id', '=', survey_complex)])
            return {
                'type': 'ir.actions.act_url',
                'name': "Results of the Survey",
                'target': 'self',
                'url': survey_complex_id.with_context(relative_url=True, purchase=True).public_url + "/" + str(self.id)}
        if survey_minor:
            survey_minor_id = survey_obj.search([('id', '=', survey_minor)])
            return {
                'type': 'ir.actions.act_url',
                'name': "Results of the Survey",
                'target': 'self',
                'url': survey_minor_id.with_context(relative_url=True, purchase=True).public_url + "/" + str(self.id)
                }
