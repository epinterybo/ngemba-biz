from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'
    
    def create_invoices(self):
        res = super().create_invoices()
        _logger.info("Pushing the log of create_invoice is %s", res)
        
        # Log the result before sanitization
        _logger.info("Original result from create_invoices: %s", res)
        
        # Sanitize the result by replacing None with safe values
        sanitized_res = self._sanitize_result(res)
        
        # Log the sanitized result
        _logger.info("Sanitized result for create_invoices: %s", sanitized_res)

        return sanitized_res
        
        
    
    def _sanitize_result(self, data):
        """
        Recursively replace None values with empty strings or another default value.
        """
        if isinstance(data, dict):
            return {k: (self._sanitize_result(v) if v is not None else '') for k, v in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_result(v) if v is not None else '' for v in data]
        else:
            return data