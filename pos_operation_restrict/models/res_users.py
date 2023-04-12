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

class res_users(models.Model):
    _inherit = "res.users"

    can_give_discount = fields.Boolean("Can Give Discount")
    can_change_price = fields.Boolean("Can Change Price")
    discount_limit = fields.Float("Discount Limit")
    can_delete_product = fields.Boolean("Pode Excluir Item")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: