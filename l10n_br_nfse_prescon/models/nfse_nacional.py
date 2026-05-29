import json

from odoo import api

from .base import PresconNfseBase
from .constants import API_ENDPOINT_NACIONAL, NFSE_URL
from .helpers import _identify_cpf_cnpj


class PresconNfseNacional(PresconNfseBase):
    """Prescon NFSe Nacional implementation."""

    _name = "prescon.nfse.nacional"
    _description = "Prescon NFSe Nacional"

    def _make_prescon_nfse_http_request(self, method, url, token, code, data=None, params=None):
        return super()._make_prescon_nfse_http_request(
            method, url, token, code, data, params
        )

    @api.model
    def process_prescon_nfse_nacional_document(self, edoc, ref, company, environment):
        token = company.prescon_production_token
        code = company.prescon_code
        if environment == "2":  # homologacao
            url = f"{NFSE_URL[environment]}{API_ENDPOINT_NACIONAL['homologacao']}"
        else:  # producao
            url = f"{NFSE_URL[environment]}{API_ENDPOINT_NACIONAL['envio']}"
        return self._make_prescon_nfse_http_request(
            "POST", url, token, code, data=edoc
        )

    @api.model
    def cancel_prescon_nfse_document(
        self, ref, cancel_reason, company, environment
    ):
        token = company.prescon_production_token
        code = company.prescon_code
        xml_envelope = f"""<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>
        <nfe>
            <cancelaNota>
                <codigoMotivo>{cancel_reason}</codigoMotivo>
                <numeroNota>{ref}</numeroNota>
            </cancelaNota>
        </nfe>"""
        url = f"{NFSE_URL[environment]}{API_ENDPOINT_NACIONAL['cancelamento']}"
        return self._make_prescon_nfse_http_request(
            "POST", url, token, code, data=xml_envelope
        )
