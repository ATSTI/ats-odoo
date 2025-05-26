# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools, api


class AllNoteReport(models.Model):
    """ Get All Notes Report """

    _name = "all.note.report"
    _auto = False
    _description = "Get All Notes Report"
    _rec_name = 'id'

    x_company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
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
    x_data_nota = fields.Date(
        string='Data da Nota',
        readonly=True,
    )

    def _select(self):
        return """
            SELECT
                min(fd.id) AS id,
                fd.company_id AS x_company_id,
                fd.document_number AS x_numero_nota, 
                fd.state_edoc AS x_status_nota,
                count(fd.id) AS x_total_nota,
                sum(fd.amount_total) AS x_valor_nota,
                CAST(fd.document_date AS DATE) AS x_data_nota
        """

    def _from(self):
        return """
            FROM l10n_br_fiscal_document fd
        """

    def _where(self):
        return """
            WHERE fd.state_edoc = 'autorizada'
        """
    
    def _group_by(self):
        return """
            GROUP BY  fd.company_id, fd.document_date, fd.document_number, fd.state_edoc
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
        """ % (self._table, self._select(), self._from(), self._where(), self._group_by())
        )