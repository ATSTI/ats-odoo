import base64
from odoo import models, fields, api
from odoo.modules.module import get_module_resource

def load_image(filename):
    path = get_module_resource('report_mm', 'static/src/img', filename)
    try:
        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except (FileNotFoundError, IOError):
        return False

class Company(models.Model):
    _inherit = 'res.company'

    instagram_png = fields.Binary(
        string='Instagram',
        compute="_compute_icons",
    )
    email_png = fields.Binary(
        string='Email',
        compute="_compute_icons",
    )
    whatsapp_png = fields.Binary(
        string='Whatsapp',
        compute="_compute_icons",
    )
    

    def _compute_icons(self):
        for company in self:
            company.instagram_png = load_image("instagram.png")
            company.email_png = load_image("email.png")
            company.whatsapp_png = load_image("whatsapp.png")
