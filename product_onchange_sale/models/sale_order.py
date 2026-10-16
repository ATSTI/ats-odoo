import logging

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_atualizar_fatura(self):
        self.ensure_one()

        invoices = self.invoice_ids.filtered(
            lambda m: m.move_type == 'out_invoice' and m.state != 'cancel'
        )

        if not invoices:
            raise UserError(_("Este pedido não possui fatura ativa para atualizar."))

        if len(invoices) > 1:
            raise UserError(_(
                "Este pedido possui mais de uma fatura ativa (%s). "
                "A atualização automática só funciona com uma fatura por pedido."
            ) % ', '.join(invoices.mapped('name')))

        invoice = invoices

        inv_by_sol = {}
        for inv_line in invoice.invoice_line_ids:
            for sol in inv_line.sale_line_ids:
                inv_by_sol.setdefault(sol.id, inv_line)

        commands = []
        kept_ids = set()
        so_sequencia = True  # vira False se algo além da ordem mudar

        for sol in self.order_line:
            vals = self._get_valores_linha_fatura(sol)
            inv_line = inv_by_sol.get(sol.id)

            if not inv_line:
                commands.append((0, 0, vals))
                so_sequencia = False
                continue

            kept_ids.add(inv_line.id)
            diff = self._diferencas_linha_fatura(inv_line, vals)

            # import pudb; pudb.set_trace()

            if diff:
                commands.append((1, inv_line.id, diff))
                if set(diff) != {'sequence'}:
                    so_sequencia = False

        for inv_line in invoice.invoice_line_ids:
            if inv_line.id not in kept_ids:
                commands.append((2, inv_line.id))
                so_sequencia = False

        _logger.info("ATUALIZAR_FATURA %s | commands=%s", invoice.name, commands)

        if not commands:
            return self._notificacao_fatura(
                _("[v2] Fatura já está igual ao pedido."),
                'info',
            )

        # Mudou só a ordem das linhas: grava direto, sem voltar para rascunho.
        if so_sequencia:
            invoice.write({'invoice_line_ids': commands})
            return self._notificacao_fatura(
                _("[v2] Ordem das linhas da fatura atualizada."),
                'success',
            )

        estava_postada = invoice.state == 'posted'

        if estava_postada:
            invoice.button_draft()

        invoice.write({'invoice_line_ids': commands})

        # if estava_postada:
        #     invoice.action_post()

        return self._notificacao_fatura(
            _("[v2] Fatura %s atualizada com sucesso.") % (invoice.name or ''),
            'success',
        )

    def _get_valores_linha_fatura(self, sol):
        vals = sol._prepare_invoice_line(sequence=sol.sequence)
        if not sol.display_type:
            # _prepare_invoice_line usa qty_to_invoice (0 se já faturado)
            vals['quantity'] = sol.product_uom_qty
        return vals

    def _diferencas_linha_fatura(self, inv_line, vals):
            dp = self.env['decimal.precision']
            prec_price = dp.precision_get('Product Price')
            prec_disc = dp.precision_get('Discount')
            prec_qty = dp.precision_get('Product Unit of Measure')

            diff = {}

            if inv_line.sequence != vals.get('sequence', inv_line.sequence):
                diff['sequence'] = vals['sequence']

            if (inv_line.name or '') != (vals.get('name') or ''):
                diff['name'] = vals.get('name') or ''

            if vals.get('display_type') in ('line_section', 'line_note'):
                return diff

            if inv_line.product_id.id != (vals.get('product_id') or False):
                diff['product_id'] = vals.get('product_id') or False

            if inv_line.product_uom_id.id != (vals.get('product_uom_id') or False):
                diff['product_uom_id'] = vals.get('product_uom_id') or False

            if float_compare(inv_line.quantity, vals.get('quantity', 0.0),
                            precision_digits=prec_qty):
                diff['quantity'] = vals.get('quantity', 0.0)

            if float_compare(inv_line.price_unit, vals.get('price_unit', 0.0),
                            precision_digits=prec_price):
                diff['price_unit'] = vals.get('price_unit', 0.0)

            if float_compare(inv_line.discount, vals.get('discount', 0.0),
                            precision_digits=prec_disc):
                diff['discount'] = vals.get('discount', 0.0)

            tax_ids = set()
            for cmd in vals.get('tax_ids') or []:
                if cmd[0] == 6:
                    tax_ids = set(cmd[2])
            if set(inv_line.tax_ids.ids) != tax_ids:
                diff['tax_ids'] = [(6, 0, list(tax_ids))]

            if (inv_line.analytic_distribution or {}) != (vals.get('analytic_distribution') or {}):
                diff['analytic_distribution'] = vals.get('analytic_distribution') or {}

            return diff

    def _notificacao_fatura(self, mensagem, tipo):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Atualizar fatura"),
                'message': mensagem,
                'type': tipo,
                'sticky': False,
                'next': {'type': 'ir.actions.client', 'tag': 'reload'},
            },
        }