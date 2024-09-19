from odoo import models


class PosSession(models.Model):
    """
    The inherited class PosSession to add new fields and models to pos.session
    """
    _inherit = 'pos.session'

    def _loader_params_hr_employee(self):
        """
        Method for loading hr_employee fields to pos.session
        :return: dictionary containing hr_employee access right fields
        """
        result = super()._loader_params_hr_employee()
        result['search_params']['fields'].extend(
            ['disable_payment', 'disable_customer', 'disable_plus_minus',
             'disable_numpad', 'disable_qty', 'disable_discount',
             'disable_price', 'disable_remove_button','disable_refund_button'])
        return result
