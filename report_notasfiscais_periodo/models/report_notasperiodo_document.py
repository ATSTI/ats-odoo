from odoo import fields, models

class ReportNotaPeriodoWizard(models.TransientModel):
    _name = 'report.notasperiodo.wizard'
    _description = 'Relatório de Notas por Período - Wizard'

    data_inicial = fields.Date(
        string='Data Inicial',
        required=True
    )

    data_final = fields.Date(
        string='Data Final',
        required=True
    )
    tipo_documento =fields.Selection([
        ("55",'NF-e'),
        ('SE','NFS-e'),
        ('65','NFC-e'),
    ], string='Tipo de Documento', required=True)

    def action_print_report(self):
        data = {
            'data_inicial': self.data_inicial,
            'data_final': self.data_final,
            'tipo_documento': self.tipo_documento
        }

        return self.env.ref(
            'report_notasfiscais_periodo.report_notasperiodo_wizard'
        ).report_action(self, data=data)