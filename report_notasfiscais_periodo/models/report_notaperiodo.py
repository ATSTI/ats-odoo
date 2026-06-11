from odoo import api, models, fields, _ 
TIPOS_DOCUMENTO = {
    '55': 'NF-e',
    'SE': 'NFS-e',
    '65': 'NFC-e',
}

class ReportNotaPeriodoWizard(models.AbstractModel):
    _name = 'report.report_notasfiscais_periodo.report_notasperiodo_document'
    _description = 'Relátório de notas por período'



    def _get_report_values(self,docids,data = None):   
        data_inicial = fields.Date.to_date(data.get('data_inicial')) if data.get('data_inicial') else None
        data_final = fields.Date.to_date(data.get('data_final')) if data.get('data_final') else None
        tipo_documento = data['tipo_documento']
        # import pudb; pudb.set_trace()
        notas_fiscais = self.env['account.move'].search([
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('state', '=', 'posted'),
            ('document_type_id.code', 'ilike', tipo_documento),
            ('invoice_date', '>=', data_inicial),
            ('invoice_date', '<=', data_final)
        ])

        return {
            'doc_ids': docids,
            'doc_model': self.env['account.move']._name,
            'data_inicial': data_inicial.strftime('%d/%m/%Y') if data_inicial else None,
            'data_final': data_final.strftime('%d/%m/%Y') if data_final else None,
            'tipo_documento': TIPOS_DOCUMENTO.get(tipo_documento),
            'notas_fiscais': notas_fiscais,
        }
            