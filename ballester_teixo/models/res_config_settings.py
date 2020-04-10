# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    teixo_user = fields.Char('Teixo User Name')
    teixo_token = fields.Char('Teixo Token')
    teixo_url = fields.Char('Teixo URL')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        cp_obj = self.env['ir.config_parameter']
        res.update(
            teixo_user=cp_obj.sudo().get_param('teixo_user') or False,
            teixo_token=cp_obj.sudo().get_param('teixo_token') or False,
            teixo_url=cp_obj.sudo().get_param('teixo_url') or False
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        cp_obj = self.env['ir.config_parameter']
        cp_obj.sudo().set_param('teixo_user', self.teixo_user)
        cp_obj.sudo().set_param('teixo_token', self.teixo_token)
        cp_obj.sudo().set_param('teixo_url', self.teixo_url)
