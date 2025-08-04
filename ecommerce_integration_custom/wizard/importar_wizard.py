# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _, api
from datetime import datetime, date
from odoo.exceptions import ValidationError
import requests


class ImportarPedidoOnline(models.TransientModel):
    _name = "importar.pedido.online"
    _description = "Importar Wizard"

    pedido_id = fields.Char('Nome arquivo')
    shopee = fields.Boolean('Shopee', default=False)
    meli = fields.Boolean('Mercado Livre', default=False)
    # shopee_config_id = fields.Many2one('shopee.config', 'Shopee')
    # meli_config_id = fields.Many2one('meli.config', 'Meli')


    def action_importar_pedido(self):
        if not self.pedido_id:
            raise ValidationError(_("O campo 'Nome arquivo' é obrigatório."))
        sale_exists = self.env['sale.order'].search([
            ('name', '=' , self.pedido_id)
        ])
        if sale_exists:
            raise ValidationError(_("Pedido Já Existe no Odoo"))
        else:
            if self.shopee:
                shopee_lj = self.env['shopee.config'].search([('name', 'ilike', 'Felicita')])
                shopee_lj.criar_pedido_shopee(self.pedido_id)
                return 
            if self.meli:
                meli_lj = self.env['meli.config'].search([('name', 'ilike', 'Felicita')])
                url = f'https://api.mercadolibre.com/orders/{self.pedido_id}'
                headers = {
                    'Authorization': f'Bearer {meli_lj.access_token}'
                }
                response = requests.get(url, headers=headers)
                if response.status_code != 200 and response.json().get('error') == "order_not_found":
                    url = f'https://api.mercadolibre.com/packs/{self.pedido_id}'
                    headers = {
                        'Authorization': f'Bearer {meli_lj.access_token}'
                    }
                    response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    for od in response.json()['orders']:
                        order = od['id']
                        meli_lj.cria_pedido_meli(order, headers)
                    return
        