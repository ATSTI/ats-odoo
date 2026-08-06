# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.tools.translate import _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class ContractLine(models.Model):
    _inherit = "contract.line"

    def _update_recurring_next_date(self):
        # isso modifica a recurring_next_date de forma q nao queremos
        pass

class ContractContract(models.Model):
    _inherit = "contract.contract"

    interval_months = fields.Integer(string="Intervalo de Cobrança (Meses)", default=1)

    @api.depends(
        "contract_line_ids.recurring_next_date",
        "contract_line_ids.is_canceled",
    )
    def _compute_recurring_next_date(self):
        for contract in self:
            if contract.active == False:
                contract.recurring_next_date = False
                continue
            interval = (contract.interval_months or 1)
            if interval < 1:
                interval = 1
            if not contract.date_start:
                contract.recurring_next_date = False
                continue
            today = fields.Date.today()
            if contract.recurring_next_date and contract.recurring_next_date > today:
                next_date = contract.recurring_next_date
            else:
                next_date = contract.date_start
            while next_date <= today:
                next_date = next_date + relativedelta(months=interval)
            if contract.date_end and next_date > contract.date_end:
                contract.recurring_next_date = False
            else:
                contract.recurring_next_date = next_date

    def _recurring_create_invoice(self, date_ref=False):
        """Cria faturas recorrentes sem depender do módulo l10n_latam, ignorando contratos cancelados ou inativos"""
        invoices_values = []
        contracts_to_invoice = self.filtered(lambda c: c.active)
        if not contracts_to_invoice:
            raise ValidationError(_("O contrato deve estar ativo e não cancelado para gerar faturas."))
        invoices_values = contracts_to_invoice._prepare_recurring_invoices_values(date_ref)
        moves = self.env["account.move"].create(invoices_values)
        contracts_to_invoice._add_contract_origin(moves)
        contracts_to_invoice._invoice_followers(moves)
        for contract in self:
            if contract.active:
                next_date = contract.recurring_next_date or contract.date_start
                next_date += relativedelta(months=contract.interval_months or 1)
                contract.write({"recurring_next_date": next_date})

        for move in moves:
            if move.amount_total> 0.01:
                move.action_post()

        return moves

    def _prepare_recurring_invoices_values(self, date_ref=False):
        """Gera os valores das faturas com base nas regras de preço sem passar pelo l10n_latam"""
        invoices_values = []
        for contract in self:
            if not contract.partner_id:
                continue
            journal = self.env['account.journal'].search([
                ('company_id', '=', contract.company_id.id),
                ('type', '=', 'sale'),
                ('l10n_latam_use_documents', '=', False)
            ], limit=1)
            if not journal:
                journal = self.env['account.journal'].create({
                    'name': 'Vendas Internas (Sem Fiscal)',
                    'code': 'INTV',
                    'type': 'sale',
                    'company_id': contract.company_id.id,
                    'l10n_latam_use_documents': False,
                })
            invoice_date = date_ref or fields.Date.today()
            mes_ano = invoice_date.strftime("%m/%Y")
            # cliente = contract.partner_id.name or "Sem Cliente"
            contrato = contract.code or str(contract.id)
            # invoice_name = f"FATURA - {cliente} - {mes_ano} - {contrato}
            dias_vencimento = int(self.payment_term_id.line_ids.payment_days)
            vencimento = self.recurring_next_date.replace(day=dias_vencimento)
            if vencimento < self.recurring_next_date:
                vencimento = vencimento + relativedelta(months=+1)
            mes_ano = vencimento.strftime("%m/%Y")
            invoice_vals = {
                "move_type": "out_invoice",
                "partner_id": contract.partner_id.id,
                "invoice_date": invoice_date,
                "ref": contrato + "-" + mes_ano,
                "company_id": contract.company_id.id,
                "journal_id": journal.id,
                "invoice_line_ids": [],
                "l10n_latam_document_type_id": False,
                "l10n_latam_document_number": False,
                # "name": invoice_name,
                "invoice_date_due": vencimento,
            }
            invoices_values.append(invoice_vals)
        return invoices_values
    
