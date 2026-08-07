import logging
from datetime import timedelta, datetime
from unidecode import unidecode
import json
import re
import os
from odoo import http
from odoo.http import request
from math import floor

_logger = logging.getLogger(__name__)

class AccessLogs(http.Controller):

    @http.route('/access_logs', type='json', auth='user', csrf=False)
    def get_access_logs(self, **kwargs):
        raw = kwargs.get("raw_response", "")
        # file = "/tmp/registros/" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".txt"
        # with open(file, "w", encoding="utf-8") as arquivo:
        #     arquivo.write(raw)
        data = self.text2json(raw)

        CondoLogs = request.env['condo.residence.logs'].sudo()
        Partner = request.env['res.partner'].sudo()
        Tags = request.env['condo.residence.tags'].sudo()
        Vehicles = request.env['condo.residence.vehicles'].sudo()

        # ---- Dados que não mudam por registro: carregados UMA vez, fora do loop ----
        desconhecido = Partner.browse(1556)
        inbox = request.env['mail.channel'].sudo().search([('name', 'ilike', 'Registros')])

        door_name_map = {
            "0": "Entrada",
            "1": "Saída",
        }

        partner_by_userid = {}
        for p in Partner.search([('UserID', '!=', False)]):
            for uid in p.UserID.split():
                partner_by_userid[uid] = p

        tag_by_card = {}
        for t in Tags.search([]):
            tag_by_card[t.numero_tag] = t

        vehicles_com_tag = Vehicles.search([('possui_tag', '=', True)])

        last_records = {}

        import pudb;pu.db
        for record in data["records"]:
            timestamp = int(record.get("CreateTime", 0))
            user_id = record.get("UserID")
            no_card = record.get("CardNo")
            no_card = str(int(no_card, 16)) if no_card else None
            if not user_id:
                continue

            door = record.get("Door")
            if not door:
                continue

            key = (user_id, door)

            if key in last_records:
                diff = timestamp - last_records[key]

                if 0 <= diff <= 30:
                    continue

            last_records[key] = timestamp

            date = datetime.fromtimestamp(timestamp) - timedelta(hours=1)
            inicio = date - timedelta(seconds=25)
            fim = date + timedelta(seconds=25)

            door_name = door_name_map.get(door, "Desconhecida")

            tag = tag_by_card.get(no_card, Tags.browse())
            morador = partner_by_userid.get(str(user_id), Partner.browse()) or tag.partner_id if tag else Partner.browse()

            vehicle = Vehicles.browse()
            if no_card is not None:
                card_str = str(no_card).lower()
                for v in vehicles_com_tag:
                    if v.numero_tag and card_str in v.numero_tag.lower():
                        vehicle = v
                        break

            if not morador and not tag:
                desconhecido_id = desconhecido.id
                # Usuario não cadastrado cria Log proprio indefinido
                log_existente = CondoLogs.search([
                    ("partner_id", "=", desconhecido_id),
                    ("num_tag", '=', no_card),
                    ("data_entrada", ">=", inicio),
                    ("data_entrada", "<=", fim),
                ], limit=1)
                if not log_existente:
                    CondoLogs.create({
                        "partner_id": desconhecido_id,
                        "num_tag": no_card,
                        "data_entrada": date,
                    })
                elif door_name == "Saída":
                    log = CondoLogs.search([
                        ("partner_id", "=", desconhecido_id),
                        ("num_tag", "=", no_card),
                        ("status", "=", "pendente"),
                    ], order="data_entrada desc", limit=1)
                    if log:
                        log.write({
                            "data_saida": date,
                        })
                if inbox:
                    msg = f'Contato da Tag {no_card} não encontrado no Odoo, faça o cadastro do Contato e das Tags\n Horario: {date}\n'
                    inbox.message_post(
                        body=msg,
                        message_type='comment',
                        author_id=request.env.ref('base.partner_root').id,
                        subtype_xml_id='mail.mt_comment'
                    )

            if morador.id in tag.mapped('partner_id').ids:
                residence = tag.residence_id
                if door_name == "Entrada":

                    log_existente = CondoLogs.search([
                        ("residence_id", "=", residence.id),
                        ("partner_id", "=", morador.id),
                        ("data_entrada", ">=", inicio),
                        ("data_entrada", "<=", fim),
                    ], limit=1)
                    if not log_existente:
                        CondoLogs.create({
                            "residence_id": residence.id,
                            "partner_id": morador.id,
                            "num_tag": no_card,
                            "vehicle_placa": vehicle.placa if vehicle else "",
                            "data_entrada": date,
                        })
                elif door_name == "Saída":
                    log = CondoLogs.search([
                        ("residence_id", "=", residence.id),
                        ("partner_id", "=", morador.id),
                        ("num_tag", "=", no_card),
                        ("status", "=", "pendente"),
                    ], order="data_entrada desc", limit=1)
                    if log:
                        log.write({
                            "data_saida": date,
                        })
                        if log.partner_id == desconhecido:
                            log.write({'partner_id': morador.id})

            _logger.info(
                "UserID: %s | Tag: %s | Data/Hora: %s | Door: %s",
                user_id, no_card, date, door_name,
            )

    def text2json(self, text):
        records = {}
        found = 0

        for line in text.splitlines():
            if "=" not in line:
                continue

            key, value = line.split("=", 1)

            if key == "found":
                found = int(value)
                continue

            m = re.match(r"records\[(\d+)\]\.(.+)", key)
            if not m:
                continue

            idx = int(m.group(1))
            field = m.group(2)

            records.setdefault(idx, {})
            records[idx][field] = value

        return {
            "found": found,
            "records": list(records.values()),
        }