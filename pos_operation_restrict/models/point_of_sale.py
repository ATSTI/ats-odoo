# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
# Please see LICENSE file.
#################################################################################

from openerp import models, fields, api, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    pos_managers_ids = fields.Many2many('res.users','posconfig_partner_rel','location_id','partner_id', string='Managers')