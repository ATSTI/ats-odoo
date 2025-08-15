# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
import requests
import time


class ProducTemplate(models.Model):
    _inherit = "product.template"

    meli = fields.Boolean(
        string='Vende Mercado Livre?',
        default=False,
        )
    meli_item_id = fields.Char('Id do Item')
    other_costs_meli = fields.Float('Outros Custos Mercado Livre', default='0')
    title_meli = fields.Char('Titulo do Produto')
    meli_sku = fields.Char('SKU Mercado Livre')
    price_meli = fields.Float('Preço Mercado Livre')
    qtd_meli = fields.Float('Quantidade Disponivel Mercado Livre')
    # category_meli = fields.Selection([
    #     # CATEGORIAS MERCADO LIVRE (VITTON)
    #     ('MLB455528', 'Agasalhos'),
    #     ('MLB188064', 'Bermudas e Shorts'),
    #     ('MLB23262', 'Calçados'),
    #     ('MLB188065', 'Calças'),
    #     ('MLB107292', 'Camisas'),
    #     ('MLB278018', 'Leggings'),
    #     ('MLB27250', 'Macacão'),
    #     ('MLB270215', 'Moda Fitness'),
    #     #TODO ADICIONAR TODAS CATEGORIAS UTILIZADAS NO MERCADO LIVRE
    # ],'Categoria Mercado Livre')
    # guarantee_meli = fields.Selection([
    #     ('0', 'Sem Garantia'),
    #     ('30', '30 dias'),
    #     ('60', '60 dias'),
    #     ('90', '90 dias'),
    #     ('120', '120 dias'),
    #     ('180', '180 dias'),
    #     ('360', '360 dias'),    ], string='Garantia do Comprador', default='0')
    # image_meli = fields.Char('Imagem Mercado Livre')
    meli_config_id = fields.Many2one('meli.config', 'Mercado Livre')

    # Formula: Vt = Pc + T + Cv + Ml
    # Pc; vem do ODOO
    # T; fixa de cada plataforma
    # Cv; Variavel (pensar como colocar isso)
    # Ml; Proavelmente fixo em 45%

    @api.depends('standard_price')
    def calcula_valor_venda_meli(self):
        #Por enquanto essa aplicação, apresentar para eles e ver...
        pc = self.standard_price
        t = self.meli_config_id.taxa_meli
        cv = self.meli_config_id.margin_meli/100 * pc
        ml = self.meli_config_id.margem_lucro/100 * pc
        Vt = pc + t + cv + ml
        self.price_meli = Vt
        if self.other_costs_meli >= 0.0:
            self.price_meli += self.other_costs_meli

    @api.onchange('other_costs_meli')
    def onchange_other_costs_meli(self):
        if self.meli == True:
            self.calcula_valor_venda_meli()

    @api.onchange('standard_price')
    def onchange_standard_price_meli(self):
        if self.meli == True:
            self.calcula_valor_venda_meli()

    @api.onchange('meli')
    def onchange_meli(self):
        if self.meli == True:
            self.title_meli = self.name
            self.meli_sku = self.default_code
            self.qtd_meli = 1
            self.calcula_valor_venda_meli()

    def encontrar_item_por_sku(self):
        user_id = self.meli_config_id.user_id
        access_token = self.meli_config_id.access_token
        sku_alvo = self.meli_sku

        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        max_iter = 2200  # limite para evitar loop infinito, ajuste conforme necessário
        iter_count = 0
        scroll_id = None
        todos_ids = []

        while True:
            url = f"https://api.mercadolibre.com/users/{user_id}/items/search?search_type=scan"
            if scroll_id:
                url += f"&scroll_id={scroll_id}"

            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print(f"Erro na busca com scroll: {response.status_code} - {response.text}")
                break

            data = response.json()
            results = data.get("results", [])
            if not results:
                break

            todos_ids.extend(results)
            scroll_id = data.get("scroll_id")
            if not scroll_id:
                break

            iter_count += 1
            if iter_count >= max_iter:
                print("Atingiu máximo de iterações, saindo do loop para evitar loop infinito.")
                break

            time.sleep(0.1)

        # 2. Processar os itens em lotes de 20
        for i in range(0, len(todos_ids), 20):
            batch_ids = todos_ids[i:i+20]
            ids_str = ",".join(batch_ids)
            url = f"https://api.mercadolibre.com/items?ids={ids_str}"
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print(f"Erro ao buscar lote de itens: {response.status_code} - {response.text}")
                continue
            results = response.json()
            for item in results:
                item_data = item.get("body", {})
                # if not item_data or item_data.get("status") != "active":
                #     continue
                item_id = item_data.get("id")
                sku_visto = False
                for att in item_data.get("attributes", []):
                    if att.get("id") == "SELLER_SKU":
                        if att.get("value_id") == sku_alvo or att.get("value_name") == sku_alvo:
                            sku_visto = True
                if item_data.get("seller_custom_field") == sku_alvo:
                    sku_visto = True
                if sku_visto:
                    self.meli_item_id = item_id
                    msg = f"Item encontrado: {item_id}"
                    return   

        print("SKU não encontrado entre os itens do usuário.")        
        raise UserError(_("SKU não encontrado entre os itens do usuário."))

    def action_envia_produto_meli(self):
        if self.meli_config_id.expire_date_token and self.meli_config_id.expire_date_token < datetime.now():
            self.meli_config_id.action_gera_acess_token()
            print("TOKEN GERADO")
        if self.meli_item_id:
            headers = {
                'Authorization': 'Bearer %s' %(self.meli_config_id.access_token),
                'Content-Type': 'application/json',
            }

            data = "{\
                status: closed}"
            data = data.encode()
            url = f'https://api.mercadolibre.com/items/{self.meli_item_id}'
            response = requests.put(url, headers=headers, data=data)
            if response.status_code == 200:
                print("PRODUTO FECHADO")
            headers = {
                'Authorization': 'Bearer %s' %(self.meli_config_id.access_token),
                'Content-Type': 'application/json',
            }

            data = '{ \
                price: %s, \
                quantity: %s, \
                listing_type_id:gold_special\
            }' %(self.price_meli, self.qtd_meli)
            data = data.encode()
            url = f'https://api.mercadolibre.com/items/{self.meli_item_id}/relist'
            response = requests.post(url, headers=headers, data=data)
            item = response.json()
            self.meli_item_id = item['id']
        else:
            self.encontrar_item_por_sku()
        insere_meli_item = False
        if insere_meli_item == True:
            import pudb;pu.db
            if not self.meli_item_id:
                variations = []
                pp = self.env['product.product'].search([('product_tmpl_id', '=', self.id),('qty_available', '>', 0)])
                for p in pp:
                    row_size = [{"id":"3189094","name":"16"},{"id":"3189096","name":"17"},{"id":"3189098","name":"18"},{"id":"3189100","name":"19"},{"id":"3259499","name":"20"},{"id":"3189104","name":"21"},{"id":"3259501","name":"22"},{"id":"3259502","name":"23"},{"id":"3189110","name":"24"},{"id":"3259521","name":"25"},{"id":"4147746","name":"26"},{"id":"3259523","name":"27"},{"id":"3259504","name":"28"},{"id":"3259505","name":"29"},{"id":"3259506","name":"30"},{"id":"3259507","name":"31"},{"id":"3189126","name":"32"},{"id":"3189128","name":"33"},{"id":"3189130","name":"34"},{"id":"4608574","name":"35"},{"id":"3259450","name":"36"},{"id":"3259511","name":"37"},{"id":"3259451","name":"38"},{"id":"3259512","name":"39"},{"id":"3189142","name":"40"},{"id":"3259513","name":"41"},{"id":"3259453","name":"42"},{"id":"3259524","name":"43"},{"id":"3259454","name":"44"},{"id":"3189152","name":"45"},{"id":"3189154","name":"46"},{"id":"3189156","name":"47"},{"id":"3189158","name":"48"},{"id":"3189160","name":"49"},{"id":"3189161","name":"50"},{"id":"6367305","name":"Único"},{"id":"3259490","name":"Sob medida"}]
                    for row in row_size:
                        if p.product_template_attribute_value_ids.name == row['name']:
                            variation = {
                                "attribute_combinations": [
                                    {
                                        "id": "SIZE",
                                        "value_name": row['name']
                                    },
                                    {
                                        "id": "SIZE_GRID_ROW_ID",
                                        "value_id": row['id']
                                    }
                                ],
                                "price": p.lst_price,
                                "available_quantity": p.qty_available,
                                "seller_custom_field": p.default_code,
                                "picture_ids": ["https://example.com/imagem.jpg"]
                            }
                            variations.append(variation)
                    # variations += '{\
                    #     "attribute_combinations": [\
                    #         {\
                    #             "id": "FOOTWEAR_SIZE",\
                    #             "value_name": "%s"\
                    #         }\
                    #     ],\
                    #     "price": %s,\
                    #     "available_quantity": %s,\
                    #     "seller_custom_field": "%s",\
                    #     "picture_ids": ["https://example.com/imagem.jpg"]\
                    # },' %(p.product_template_attribute_value_ids.name, p.lst_price, p.qty_available, p.default_code)

                # for va in self.attribute_line_ids:
                #     if va.attribute_id.name == 'Tamanho Roupas' or va.attribute_id.name == 'Tamanho Calçados':
                #         for value in va.value_ids:
                #REMOVIDO DO DATDA: "available_quantity":%s,\
                import pudb;pu.db
                headers = {
                    'Authorization': 'Bearer %s' %(self.meli_config_id.access_token),
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
                data = '{  \
                    "title":%s,\
                    "category_id": MLB23332,\
                    "price":%s,\
                    "currency_id":"BRL",\
                    "buying_mode":"buy_it_now",\
                    "condition":"new",\
                    "listing_type_id":"gold_special",\
                    "sale_terms":[\
                        {\
                            "id":"WARRANTY_TYPE",\
                            "value_name":"Garantia do vendedor"\
                        },\
                        {\
                            "id":"WARRANTY_TIME",\
                            "value_name":"%s Dias"   \
                        }\
                    ],\
                    "pictures":[{\
                        "source":"https://example.com/imagem.jpg"\
                        }\
                    ], \
                    "variations": %s,\
                    "attributes":[\
                        {\
                            "id":"BRAND",\
                            "value_name":"Sem Marca"\
                        },\
                        {\
                            "id": "MODEL",\
                            "value_name": "Tênis Casual"\
                        },\
                        {\
                            "id": "GENDER",\
                            "value_name": "Sem gênero" \
                        },\
                    ],\
                    "shipping": {\
                        "mode": "me2",\
                        "local_pick_up": false,\
                        "free_shipping": false\
                    },\
                    "seller_custom_field": "%s"\
                }' %(self.title_meli, self.price_meli, self.guarantee_meli, variations,self.meli_sku)
                data = data.encode() 
                response = requests.post('https://api.mercadolibre.com/items', headers=headers, data=data)
                item = response.json()
                print (item)
                # self.meli_item_id = item['id']
