# -*- coding: utf-8 -*-

from odoo import http, SUPERUSER_ID
from odoo.http import request
import io
import xlsxwriter
from datetime import datetime

header_name = [
    'Order Number',
    'Order Date',
    'Order Description',
    'Customer Name',
    'Shipping Address',

    'Dress Code',
    'Color ',

    'invoice Number',
    'invoice date',
    'invoice amount',
    'invoice state',

    'payment state',
    'amount paid',
    'amount total',
    'amount residual',
]


class PartnerExcelReportController(http.Controller):
    @http.route(['/sale_xlxs_report/<string:start_date>/<string:end_date>/<model("res.partner"):partner_id>'],
                type='http',
                auth="user", csrf=False)
    def get_sale_excel_report(self, start_date=None, partner_id=None, end_date=None, **args):
        """ This function is used to get the xlxs report
            @param : start_date, end_date, partner_ids
            @return : response of the report in xlxs format """
        header_style, line_style, output, report_lines, response, sheet, workbook = self.prepare_response(end_date,
                                                                                                          partner_id,
                                                                                                          start_date)
        self.create_sheet_header(header_name, header_style, sheet)
        row = 1
        self.create_sheet_data(report_lines, line_style, sheet, row)
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        return response

    def prepare_response(self, end_date, partner_id, start_date):
        """ This function is used to prepare the response
            @param : end_date, partner_ids, start_date
            @return : header_style, line_style, output, report_lines, response, sheet, workbook
            """
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', 'Invoice_report' + '.xlsx')
            ]
        )
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        header_style, line_style, workbook = self.format_workbook(workbook)
        report_lines = request.env['sale.xlxs.report'].get_sale_order_list(start_date, end_date, partner_id)
        sheet = workbook.add_worksheet("SALES REPORT")
        return header_style, line_style, output, report_lines, response, sheet, workbook

    def create_sheet_data(self, report_lines, line_style, sheet, row):
        """ This function is used to create the sheet data"""
        self._prepare_order_data(line_style, report_lines, row, sheet)

    def _prepare_order_data(self, line_style, report_lines, row, sheet):
        """ This function is used to prepare the order data
            @param : line_style, report_lines, row, sheet
            @return : row"""
        for sale_order in report_lines:
            sheet.write(row, 0, sale_order.get('order_name'), line_style)
            sheet.write(row, 1, sale_order.get('order_date'), line_style)
            sheet.write(row, 2, sale_order.get('order_note'), line_style)
            sheet.write(row, 3, sale_order.get('partner_name'), line_style)
            sheet.write(row, 4, sale_order.get('partner_address'), line_style)
            row_line = 0
            for order_line in sale_order.get('order_line_ids'):
                row_line = row
                sheet.write(row_line, 5, order_line.get('product_name'), line_style)
                sheet.write(row_line, 6, order_line.get('product_color'), line_style)
                row_line += 1
            for invoice in sale_order.get('invoice_ids'):
                sheet.write(row, 7, invoice.get('invoice_name'), line_style)
                sheet.write(row, 8, invoice.get('invoice_date'), line_style)
                sheet.write(row, 9, invoice.get('invoice_amount'), line_style)
                sheet.write(row, 10, invoice.get('invoice_state'), line_style)
                sheet.write(row, 11, invoice.get('payment_state'), line_style)
                sheet.write(row, 12, invoice.get('amount_paid'), line_style)
                sheet.write(row, 13, invoice.get('amount_total'), line_style)
                sheet.write(row, 14, invoice.get('amount_residual'), line_style)
                row += 1

            row += 1

    def format_workbook(self, workbook):
        """ This function is used to format the workbook
            @param workbook: workbook of the xlxs
            @return: header_style: style of the header
            @return: line_style: style of the line
            @return: workbook: workbook of the xlxs
            """
        header_style = workbook.add_format(
            {'bold': True, 'font_color': 'black', 'font_size': 14, 'align': 'center', 'bg_color': '#D3D3D3'})
        workbook.set_size(100, 30)
        line_style = workbook.add_format({'font_color': 'black', 'font_size': 12})
        return header_style, line_style, workbook

    def create_sheet_header(self, header_name, header_style, sheet):
        """ This function is used to create the sheet header
            @param header_style: style of the header
            @param sheet: sheet of the workbook
            """
        for name in header_name:
            sheet.write(0, header_name.index(name), name, header_style)
