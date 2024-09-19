from odoo import fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    is_customs_bill = fields.Boolean('Is Customs Bill', default=False)
    is_shipping_bill = fields.Boolean('Is Shipping Bill', default=False)



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    harmonized_code_id = fields.Many2one(related='product_id.harmonized_code_id', store=True, readonly=True,
                                     help="Harmonized System Code, used to classify a product in import/export trade.")
