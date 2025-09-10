import os
from io import BytesIO
from PIL import Image
from odoo import models, tools, fields

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def get_email_icon(self):
        module_path = os.path.dirname(os.path.dirname(__file__)) 
        img_path = os.path.join(module_path, 'static/src/img/email.png')
        img = Image.open(img_path)
        img_base64 = tools.image_to_base64(img, output_format='PNG')
        return img_base64
    
    whatsapp_icon = fields.Binary(
        "WhatsApp Icon",
        default=lambda self: self._get_whatsapp_icon()
    )

    def _get_whatsapp_icon(self):
        module_path = os.path.dirname(os.path.dirname(__file__))
        img_path = os.path.join(module_path, 'static/src/img/whatsapp.png')
        
        # Converter a imagem para base64
        return tools.image_to_base64(img_path, output_format='PNG')
    
    def get_insta_icon(self):
        module_path = os.path.dirname(os.path.dirname(__file__)) 
        img_path = os.path.join(module_path, 'static/src/img/instagram.png')
        img = Image.open(img_path)
        img_base64 = tools.image_to_base64(img, output_format='PNG')
        return img_base64