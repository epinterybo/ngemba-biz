from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    def action_post(self):
        res = super().action_post()
        
        _logger.info("Pushing the log of AccountMove action_post  is %s", res)
        
        # Log the result before sanitization
        _logger.info("Original result from AccountMove action_post : %s", res)
        
        # Sanitize the result by replacing None with safe values
        sanitized_res = self._sanitize_result(res)
        
        # Log the sanitized result
        _logger.info("Sanitized result for AccountMove action_post: %s", sanitized_res)
        
        
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