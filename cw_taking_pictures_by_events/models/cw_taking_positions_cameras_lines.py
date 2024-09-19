from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class CwTakingPositionsCameras(models.Model):
    _name = 'cw.taking.positions.cameras.lines'
    _description = 'CW Taking Positions Cameras Lines'

    cw_taking_positions_cameras_id = fields.Many2one('cw.taking.positions.cameras', string="Camera Position")
    camera_url = fields.Char(string='Camera URL')