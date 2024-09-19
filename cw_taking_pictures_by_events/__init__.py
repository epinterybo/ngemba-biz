# -*- coding: utf-8 -*-

from . import controllers
from . import models
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    _logger.info("post_init_hook Method Called")
    from .models.cw_event_manager_listener import register_event_listener
    register_event_listener(env)
