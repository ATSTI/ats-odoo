# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""Constants for PRESCON NFSe integration."""

NFSE_URL = {
    "1": "https://arturnogueira.presconinformatica.com.br/ords/arthur",
    "2": "https://arturnogueira.presconinformatica.com.br/ords/arthur",
}

API_ENDPOINT_NACIONAL = {
    "homologacao": "/ws/nfe/simula_nfe",
    "envio": "/ws/nfe/emitir_nfe",
    "cancelamento": "/ws/nfe/cancelar_nota",
}

TIMEOUT = 60  # 60 seconds

# Constants for document status
STATUS_AUTORIZADO = "autorizado"
STATUS_CANCELADO = "cancelado"
STATUS_ERRO_AUTORIZACAO = "erro_autorizacao"
STATUS_PROCESSANDO_AUTORIZACAO = "processando_autorizacao"
CODE_NFE_CANCELADA = "nfe_cancelada"
CODE_NFE_AUTORIZADA = "nfe_autorizada"

# CPF/CNPJ length constants
CPF_LENGTH = 11
CNPJ_LENGTH = 14

# PDF validation constants
PDF_HEADER = b"%PDF-"
PDF_FOOTER = b"%%EOF"
