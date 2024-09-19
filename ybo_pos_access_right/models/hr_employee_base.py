from odoo import fields, models


class HrEmployeeBase(models.AbstractModel):
    """The inherited class HrEmployee to add new fields to 'hr.employee' """
    _inherit = "hr.employee.base"

    disable_payment = fields.Boolean(
        string="POS-Disable Payment",
        help="Disable the payment button on the POS")
    disable_customer = fields.Boolean(
        string="POS-Disable Customer",
        help="Disable the customer selection button on the POS")
    disable_plus_minus = fields.Boolean(
        string="POS-Disable Plus-Minus",
        help="Disable the +/- button on the POS")
    disable_numpad = fields.Boolean(
        string="POS-Disable Numpad",
        help="Disable the number pad on the POS")
    disable_qty = fields.Boolean(
        string="POS-Disable Qty",
        help="Disable the Qty button on the POS")
    disable_discount = fields.Boolean(
        string="POS-Disable Discount",
        help="Disable the %Disc button on the POS")
    disable_price = fields.Boolean(
        string="POS-Disable price",
        help="Disable the %Price button on the POS")
    disable_remove_button = fields.Boolean(
        string="POS-Disable Remove Button",
        help="Disable the back button on the POS")
    disable_refund_button = fields.Boolean(
        string="POS-Disable Refund Button",
        help="Disable the refund button on the POS")
