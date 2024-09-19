from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    """
    picture_file_path = fields.Char(string="Picture File Path", readonly=True, default=False)
    picture_url = fields.Char(string="Picture URL", compute="_compute_picture_url")
    picture_data = fields.Binary(string="Picture", compute="_compute_picture_data", store=False)
    """
    cw_taken_picture_details_ids = fields.One2many('cw.taken.picture.details', 'stock_picking_id', string='Camera pictures')
    
    def _action_done(self):
        res = super()._action_done()
        
        for picking in self:
            if picking.picking_type_id.code == 'outgoing':
                camera_position = self.env['cw.taking.positions.cameras'].search([
                    ('stock_location_id', '=', picking.location_id.id)
                ], limit=1)
                
                if camera_position:
                    camera_position_lines = camera_position.cw_taking_positions_cameras_lines_ids
                    """
                    x_images_lines = self.env['x_image_relations_line'].search([
                    ('x_studio_parent_record', '=', image_relation.id)
                    ])
                    """
                    
                    if camera_position_lines:
                        self.env['cw.event.manager.listener']
                        event_manager = self.env['cw.event.manager.listener']
                        
                        for camera_position_line in camera_position_lines:
                            _logger.info("Emitting event with info model_name: %s, model_id: %s", self._inherit, self.id)
                            event_manager.emit_event(event_name='image_should_be_taken', model_name=self._name, model_id=self.id, image_url=camera_position_line.camera_url)
                
                """
                picking.location_id
                
                for move in picking.move_line_ids:
                    _logger.info("Counting Product name %s with quantity %s", move.product_id.name, move.quantity)
                    self._product_scan_action(move.product_id.id, move.quantity)
                #for move in picking.move_l
                """
            
        
        return res
    
    def _product_scan_action(self, product_id, quantity):
        _logger.info("Picking Product called at this stage")
        _logger.info("Picking product id is %s", product_id)
        # Custom action to be performed on product scan
        product = self.env['product.product'].browse(product_id)
        
    