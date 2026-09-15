import math
from odoo import models, fields


class ReportMultaJurosCupom(models.AbstractModel):
    _name = 'report.report_multajuros.report_multa_juros'
    _description = 'Recibo de Multa e Juros - Cupom'

    def _compute_multa_juros(self, move):
        hoje = fields.Date.context_today(self)
        vencimento = move.invoice_date_due or move.invoice_date

        dias_atraso = 0
        meses_atraso = 0
        if vencimento and hoje > vencimento:
            dias_atraso = (hoje - vencimento).days
            meses_atraso = math.ceil(dias_atraso / 30.0)

        valor_base = move.amount_total
        valor_multa = valor_base * 0.10 if dias_atraso > 0 else 0.0
        valor_juros = valor_base * 0.01 * meses_atraso
        valor_total_final = valor_base + valor_multa + valor_juros

        return {
            'hoje': hoje.strftime('%d/%m/%Y') if hoje else "",
            'vencimento': vencimento.strftime('%d/%m/%Y') if vencimento else "",
            'dias_atraso': dias_atraso,
            'meses_atraso': meses_atraso,
            'valor_multa': valor_multa,
            'valor_juros': valor_juros,
            'valor_total_final': valor_total_final,
        }

    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        multa_data = {move.id: self._compute_multa_juros(move) for move in docs}
        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': docs,
            'multa_data': multa_data,
        }