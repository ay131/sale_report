from datetime import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleXlxsReport(models.Model):
    _name = 'sale.xlxs.report'
    _description = 'Sale Xlxs Report'

    start_date = fields.Date(string="From")
    end_date = fields.Date(string="To")
    partner_id = fields.Many2one('res.partner', string="Customer")

    @api.onchange('start_date')
    def _onchange_start_date(self):
        """ This function is used to check the start date is less than date today"""
        if self.start_date:
            if self.start_date > fields.Date.today():
                raise ValidationError("Start date must be less than date today")

    @api.onchange('end_date')
    def _onchange_end_date(self):
        """ This function is used to check the end date is less than date today"""
        if self.end_date:
            if self.end_date > fields.Date.today():
                raise ValidationError("End date must be less than date today")

    @api.onchange('start_date', 'end_date')
    def _onchange_date(self):
        """ This function is used to check the end date is greater than start date"""
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError("End date must be greater than start date")

    def generate_xlxs_report(self):
        """ This function is used to get the xlxs report """

        return {
            'name': 'Sales Report',
            'type': 'ir.actions.act_url',
            'url': '/sale_xlxs_report/%s/%s/%s' % (self.start_date, self.end_date, self.partner_id.id),
            'target': 'new',
        }

    @api.model
    def get_sale_order_list(self, start_date, end_date, partner_id):
        """ This function is used to get the order list
            @param : start_date, end_date, partner_id
            @return : lines
            """
        lines = []
        order_list = self.env['sale.order'].search(
            [('date_order', '>=', start_date), ('date_order', '<=', end_date), ('partner_id', '=', partner_id.id)])
        for order in order_list:
            order_date = datetime.strftime(order.date_order, '%Y-%m-%d %H:%M:%S')
            partner_address = " ".join(order.partner_id.contact_address.splitlines())
            if order.note:
                order_note = order.note
            else:
                order_note = "No Note"

            line = {
                'order_name': order.name,
                'order_date': order_date,
                'order_note': order_note,
                'partner_name': order.partner_id.name,
                'partner_address': partner_address,
            }
            order_line_list = []
            order_invoice_list = []
            for order_line in order.order_line:
                product_name = order_line.product_id.name
                product_color = order_line.product_id.color or "No Color"
                order_line_list.append({
                    'product_name': product_name,
                    'product_color': product_color,

                })
            for invoice in order.invoice_ids:
                payment_state = dict(invoice._fields['payment_state'].selection).get(invoice.payment_state)
                state = dict(invoice._fields['state'].selection).get(invoice.state)
                invoice_date = datetime.strftime(invoice.date, '%Y-%m-%d %H:%M:%S')
                order_invoice_list.append({
                    'invoice_name': invoice.name,
                    'invoice_date': invoice_date,
                    'invoice_amount': invoice.amount_total,
                    'invoice_state': state,
                    'payment_state': payment_state,
                    'amount_paid': invoice.amount_total_signed - invoice.amount_residual_signed,
                    'amount_total': invoice.amount_total,
                    'amount_residual': invoice.amount_residual,
                })
            line.update({'invoice_ids': order_invoice_list})
            line.update({'order_line_ids': order_line_list})
            lines.append(line)
        return lines
