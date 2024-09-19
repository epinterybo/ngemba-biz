from odoo import _, api, fields, models
import logging
from pprint import pformat

_logger = logging.getLogger(__name__)


class LoyaltyReward(models.Model):
    _inherit = ['loyalty.reward']

    allowed_total_points = fields.Float(string='Allowed Total Points')