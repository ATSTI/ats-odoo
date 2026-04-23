# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, _


class DocumentCancelWizard(models.TransientModel):
    _inherit = "l10n_br_fiscal.document.cancel.wizard"

    motivo_cancelamento = fields.Selection(
        selection=[
            ("1", "1 - ERRO - DUPLICIDADE"),
            ("2", "2 - ERRO - MES COMPETENCIA"),
            ("3", "3 - ERRO - LOCAL DA PRESTACAO"),
            ("4", "4 - ERRO - ALIQUOTA"),
            ("5", "5 - ERRO - BASE DE CALCULO"),
            ("6", "6 - ERRO - DESCRICAO DOS SERVICOS"),
            ("7", "7 - ERRO - DIVERGENCIA CADASTRAL"),
            ("8", "8 - ERRO - DADOS DO TOMADOR"),
            ("9", "9 - ERRO - ISS TOMADOR/PRESTADOR"),
            ("10", "10 - ERRO - NAO HOUVE A PRESTACAO DO SERVICO"),
            ("11", "11 - SUBSTITUICAO DE NOTA FISCAL ELETRONICA"),
            ("20", "20 - NÃO RETENCAO DO IRRF"),
            ("21", "21 - ERRO NO FATURAMENTO"),
            ("22", "22 - VALOR ERRADO"),
            ("23", "23 - NFS-E EMITIDA ERRONEAMENTE"),
            ("24", "24 - NFS-E EMITIDA INDEVIDAMENTE"),
            ("25", "25 - ERRO ADMINISTRATIVO"),
            (
                "26",
                "26 - ALTERAÇÃO DO CODIGO DE ATIVIDADE DO PRESTADOR.",
            ),
        ],
        string="Motivo do Cancelamento",
    )

    def do_cancel(self):
        if self.motivo_cancelamento:
            self.justification = self.motivo_cancelamento
        self.document_id._document_cancel(self.justification)

    def doit(self):
        for wizard in self:
            if wizard.document_id:
                wizard.do_cancel()
        self._close()
