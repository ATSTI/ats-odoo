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

            morador = Partner.search([('UserID', '=', user_id)], limit=1)
            if morador and morador.condo_residence_ids:
                residence = morador.condo_residence_ids[0]
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
                            "data_entrada": date,
                        })
                elif door_name == "Saída":
                    log = CondoLogs.search([
                        ("residence_id", "=", residence.id),
                        ("partner_id", "=", morador.id),
                        ("status", "=", "pendente"),
                    ], order="data_entrada desc", limit=1)
                    if log:
                        log.write({
                            "data_saida": date,
                        })
            print(
                "UserID:", user_id,
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