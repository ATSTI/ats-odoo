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
        data = self.text2json(raw)

        CondoLogs = request.env['condo.residence.logs'].sudo()
        Partner = request.env['res.partner'].sudo()

        last_records = {}

        for record in data["records"]:
            timestamp = int(record.get("CreateTime", 0))
            user_id = record.get("UserID")
            no_card = record.get("CardNo")
            no_card = int(no_card, 16) if no_card else None
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

            date = datetime.fromtimestamp(timestamp) + timedelta(hours=3)

            door_name = {
                "0": "Entrada",
                "1": "Saída",
            }.get(door, "Desconhecida")

            partners = Partner.search([])
            morador = partners.filtered(
                lambda p: p.UserID and str(user_id) in p.UserID.split()
            )
            tag = request.env['condo.residence.tags'].search([('numero_tag', '=', no_card)])
            if not morador or not tag:
                inbox = request.env['mail.channel'].sudo().search([('name', 'ilike', 'Registros')])
                if inbox:
                    msg = f'Contato da Tag {no_card} não encontrado no Odoo, faça o cadastro do Contato e das Tags\n'
                    inbox.message_post(
                        body=msg,
                        message_type='comment',    
                        author_id=request.env.ref('base.partner_root').id,    
                        subtype_xml_id='mail.mt_comment'
                    )
            if morador.id in tag.mapped('partner_id').ids:
                if tag and tag.residence_id:
                    residence = tag[0].residence_id
                if door_name == "Entrada":
                    inicio = date - timedelta(seconds=15)
                    fim = date + timedelta(seconds=15)

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
            print(
                "UserID:", user_id,
                "\n Tag:", no_card,
                "\nData/Hora:", date,
                "\nDoor:", door_name,
                "\n==============================="
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