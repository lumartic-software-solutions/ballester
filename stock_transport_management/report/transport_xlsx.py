# -*- coding: utf-8 -*-
# Odoo, Open Source  Stock Transport Management.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsxAbstract
import datetime
from odoo import models


class TransportReportXls(models.AbstractModel):
    _name = 'report.stock_transport_management.transport_report_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        datas = {'ids': lines.id}
        datas['model'] = 'vehicle.status'
        datas['form'] = lines.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        logged_users = self.env['res.company']._company_default_get('sale.order')
        sheet = workbook.add_worksheet()
        format1 = workbook.add_format({'font_size': 16, 'align': 'vcenter', 'bg_color': '#D3D3D3', 'bold': True})
        format1.set_font_color('#000080')
        format2 = workbook.add_format({'font_size': 12, 'bold': True, 'bg_color': '#D3D3D3'})
        format3 = workbook.add_format({'font_size': 10, 'bold': True})
        format4 = workbook.add_format({'font_size': 10})
        format1.set_align('center')
        format2.set_align('center')
        format3.set_align('center')
        sheet.merge_range('A3:L3', "Transportation Report", format1)
        report_date = datetime.datetime.now().strftime("%m/%d/%Y")
        sheet.merge_range('K1:L1', report_date, format4)
        sheet.merge_range('A1:B1', logged_users.name, format4)
        if datas['form']['start_date']:
            date_start = datas['form']['start_date']
        else:
            date_start = ""
        if datas['form']['end_date']:
            date_end = datas['form']['end_date']
        else:
            date_end = ""
        if date_start:
            sheet.write('A5', "Date From :", format3)
            sheet.write('A6', date_start, format4)
        if date_end:
            sheet.write('C5', "Date To :", format3)
            sheet.write('C6', date_end, format4)
        sheet.merge_range('A8:B8', "Vehicle Name ", format2)
        sheet.merge_range('C8:D8', "Date", format2)
        sheet.merge_range('E8:F8', "Sale Order", format2)
        sheet.merge_range('G8:H8', "Delivery Order", format2)
        sheet.merge_range('I8:J8', "No of Parcels", format2)
        sheet.merge_range('K8', "Status", format2)
        if date_start and date_end:
            report_obj = self.env['vehicle.status'].search([('transport_date', ">=", date_start) and
                                                            ('transport_date', "<=", date_end)])
        else:
            report_obj = self.env['vehicle.status'].search([])
        row_number = 9
        col_number = 0
        for values in report_obj:
            sheet.merge_range(row_number, col_number, row_number, col_number + 1, values['name'], format3)
            sheet.merge_range(row_number, col_number + 2, row_number, col_number + 3, values['transport_date'], format3)
            sheet.merge_range(row_number, col_number + 4, row_number, col_number + 5,  values['order'], format3)
            sheet.merge_range(row_number, col_number + 6, row_number, col_number + 7, values['delivery_order'], format3)
            sheet.merge_range(row_number, col_number + 8, row_number, col_number + 9, values['no_parcels'], format3)
            sheet.write(row_number, col_number + 10, values['state'], format3)
            row_number += 1

