#-*- coding: utf-8 -*-
# Odoo, Open Source Ballester Hr Attendance.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).# 

from odoo import fields, models
     
# new fields 
class resusers(models.Model):
    _inherit = 'res.users'
     
    menu_access_user = fields.Boolean(string="Menu Access User")

    
