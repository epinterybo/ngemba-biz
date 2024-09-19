from odoo import _, api, fields, models, tools 
from odoo.exceptions import UserError, ValidationError

class StockPicking(models.Model):

    _inherit = 'stock.picking'

    def action_assign(self):
        categ = self.env['res.partner.category'].search([('name','=','invoice')], limit=1)
        if categ.id not in self.sale_id.partner_id.category_id.ids:
            if self.picking_type_id.code == 'outgoing':
                if self.sale_id.total_payement < self.sale_id.amount_total:
                    raise ValidationError(_('Unable to validate this order which has not yet been paid !'))
        result = super().action_assign()
        return result

    @api.model
    def create(self, values):
        result = super().create(values)
        for move_ids_without_package in result.move_ids_without_package:
            move_ids_without_package._action_assign()
        for move_line_ids_without_package in result.move_line_ids_without_package:
            move_line_ids_without_package._action_assign()
        for line in result.move_line_ids:
            line._action_assign()

        result.action_confirm()
        if result.state in ['waiting','confirmed']:
           result.action_assign() 

        return result
