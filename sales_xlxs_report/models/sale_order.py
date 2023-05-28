from odoo import models, fields, api


# inherit sale order
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_open_wizard_form(self):
        """ This function is used to get the xlxs report """
        # print("action_open_wizard_form")
        return {
            'name': 'Sales Report',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.xlxs.report',
            'view_mode': 'form',
            'target': 'new',
        }


