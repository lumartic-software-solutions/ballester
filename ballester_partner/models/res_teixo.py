# -*- coding: utf-8 -*-
# Odoo, Open Source Ballester Sales.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models,fields

class ResTeixo(models.Model):
    _name = 'res.teixo'

    name = fields.Char(string='Name',required=True)
    token = fields.Char(string="Token",required=True)
