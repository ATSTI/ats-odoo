# Copyright 2012 - 2013 Daniel Reis
# Copyright 2015 - Antiun Ingeniería S.L. - Sergio Teruel
# Copyright 2016 - Tecnativa - Vicent Cubells
# Copyright 2018 - Brain-tec AG - Carlos Jesus Cebrian
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Task(models.Model):
    """Added Material Used in the Project Task."""

    _inherit = "project.task"

    material_ids = fields.One2many(
        comodel_name="project.task.material",
        inverse_name="task_id",
        string="Material Used",
    )
    valor_total = fields.Float(
            string="Valor Total",
            compute="_compute_total_value_id",
        )
          
    def _compute_total_value_id(self):
        total = 0.0
        for linha in self.material_ids:
            total += linha.total_item
        self.valor_total = total


class ProjectTaskMaterial(models.Model):
    """Added Product and Quantity in the Task Material Used."""

    _name = "project.task.material"
    _description = "Task Material Used"

    task_id = fields.Many2one(
        comodel_name="project.task", string="Task", ondelete="cascade", required=True
    )
    product_id = fields.Many2one(
        comodel_name="product.product", string="Product", required=True
    )
    quantity = fields.Float(
            string="Quantidade" ,
            default=1  ,                  
        )
    total_item = fields.Float(
            string="Total",
            compute="_compute_total_id",
        )
    preco_unit= fields.Float(
        string="Valor Unit.",
        readonly=False,
        store=True)

    @api.constrains("quantity")
    def _check_quantity(self):
        for material in self:
            if not material.quantity > 0.0:
                raise ValidationError(
                    _("Quantity of material consumed must be greater than 0.")
                )
    
    @api.depends("preco_unit", "quantity")      
    def _compute_total_id(self):
        for item in self:
            if item.preco_unit > 0.0:
                item.total_item = item.preco_unit * item.quantity
            else:
                item.total_item = 0.0
    
    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.product_id:
            self.preco_unit = self.product_id.standard_price
    