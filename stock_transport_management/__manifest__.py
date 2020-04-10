# -*- coding: utf-8 -*-
# Odoo, Open Source  Stock Transport Management.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "Stock Transport Management",
    'version': '11.0.2.0.0',
    'summary': """Manage Stock Transport Management With Ease""",
    'description': """This Module Manage Transport Management Of Stocks""",
    'author': 'ITMusketeers Consultancy Services LLP',
    'category': 'Warehouse',
    'depends': ['purchase','base','sale_management', 'sale', 'sales_team',  'stock', 'report_xlsx','fleet'],
    'data': [
        'security/ir.model.access.csv',
        'views/vehicle_menu_view.xml',
        'views/transport_vehicle_status_view.xml',
        'views/transportation_sale_order_view.xml',
        'views/transportation_purchase_order_view.xml',
        'views/transport_warehouse_view.xml',
        'views/transport_wizard_view.xml',
        'views/fleet_vehicle_view.xml',
        'transport_report.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
