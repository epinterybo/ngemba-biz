from odoo import models, fields, api, _
from odoo.tools import float_is_zero, float_compare
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class Picking(models.Model):
    _inherit = 'pos.order'