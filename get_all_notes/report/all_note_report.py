# -*- coding: utf-8 -*-
from odoo import fields, models, tools

class AllNoteReport(models.Model):
    _name = "all.note.report"
    _auto = False
    _description = "Get All Notes Report"
    _rec_name = 'id'

    x_company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        readonly=True,
    )

    x_mes = fields.Char(
        string='Mês/Ano',
        readonly=True,
    )

    x_numero_nota = fields.Char(
        string='Número da Nota',
        readonly=True,
    )

    x_status_nota = fields.Selection(
        selection=[
            ('autorizada', 'Autorizada'),
            ('cancelada', 'Cancelada'),
            ('denegada', 'Denegada'),
            ('inutilizada', 'Inutilizada'),
        ],
        string='Status da Nota',
        readonly=True,
    )

    x_total_nota = fields.Integer(
        string='Total de Notas',
        readonly=True,
    )

    x_valor_nota = fields.Float(
        string='Valor da Nota',
        readonly=True,
    )

    x_total_bruto = fields.Float(
        string='Total Bruto',
        readonly=True,
    )

    x_data_nota = fields.Date(
        string='Data da Nota',
        readonly=True,
    )

    x_operacao_fiscal = fields.Many2one(
        comodel_name='l10n_br_fiscal.operation',
        string='Operação Fiscal',
        readonly=True,
    )

    x_data_vencimento = fields.Date(
        string='Data de Vencimento',
        readonly=True,
    )

    def _select(self):
        return """
            SELECT
                fd.id AS id,
                fd.company_id AS x_company_id,
                to_char(fd.document_date, 'YYYY-MM') AS x_mes,
                fd.document_number AS x_numero_nota,
                fd.state_edoc AS x_status_nota,
                count(fd.id) AS x_total_nota,
                fd.amount_total AS x_valor_nota,
                fd.amount_price_gross AS x_total_bruto,
                CAST(fd.document_date AS DATE) AS x_data_nota,
                fd.fiscal_operation_id AS x_operacao_fiscal,
                am.invoice_date_due AS x_data_vencimento
        """

    def _from(self):
        return """
            FROM l10n_br_fiscal_document fd
            LEFT JOIN account_move am ON am.fiscal_document_id = fd.id
        """

    def _where(self):
        return """
            WHERE fd.state_edoc = 'autorizada'
        """

    def _group_by(self):
        return """
            GROUP BY
                fd.id,
                fd.company_id,
                fd.document_date,
                fd.document_number,
                fd.state_edoc,
                fd.amount_total,
                fd.amount_price_gross,
                fd.fiscal_operation_id,
                am.invoice_date_due
        """

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                %s
                %s
                %s
                %s
            )
        """ % (
            self._table,
            self._select(),
            self._from(),
            self._where(),
            self._group_by()
        ))