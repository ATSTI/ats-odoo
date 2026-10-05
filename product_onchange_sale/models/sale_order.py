from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


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

        # Mapa: linha do pedido -> linha da fatura
        inv_by_sol = {}
        for inv_line in invoice.invoice_line_ids:
            for sol in inv_line.sale_line_ids:
                inv_by_sol.setdefault(sol.id, inv_line)

        commands = []
        kept_ids = set()

        for sol in self.order_line:
            vals = self._get_valores_linha_fatura(sol)
            inv_line = inv_by_sol.get(sol.id)

            if inv_line and self._linha_fatura_confere(inv_line, vals):
                kept_ids.add(inv_line.id)
                if inv_line.sequence != vals['sequence']:
                    commands.append((1, inv_line.id, {'sequence': vals['sequence']}))
                continue

            if inv_line:
                commands.append((2, inv_line.id))
                kept_ids.add(inv_line.id)  # já tratada (excluída para recriar)
            commands.append((0, 0, vals))

        # Linhas da fatura sem correspondência no pedido (removidas do pedido
        # ou adicionadas manualmente na fatura)
        for inv_line in invoice.invoice_line_ids:
            if inv_line.id not in kept_ids:
                commands.append((2, inv_line.id))

        # Nada mudou: não mexe na fatura
        if not any(c[0] in (0, 2) for c in commands) and not commands:
            return self._notificacao_fatura(
                _("Fatura já está igual ao pedido."), 'info')
        if not any(c[0] in (0, 2) for c in commands):
            # só sequência mudou
            invoice.write({'invoice_line_ids': commands})
            return self._notificacao_fatura(
                _("Ordem das linhas da fatura atualizada."), 'success')

        estava_postada = invoice.state == 'posted'
        if estava_postada:
            invoice.button_draft()

        invoice.write({'invoice_line_ids': commands})

        if estava_postada:
            invoice.action_post()

        return self._notificacao_fatura(
            _("Fatura %s atualizada com sucesso.") % (invoice.name or ''), 'success')

    def _get_valores_linha_fatura(self, sol):
        vals = sol._prepare_invoice_line(sequence=sol.sequence)
        if not sol.display_type:
            # _prepare_invoice_line usa qty_to_invoice (0 se já faturado)
            vals['quantity'] = sol.product_uom_qty
        return vals

    def _linha_fatura_confere(self, inv_line, vals):
        dp = self.env['decimal.precision']
        prec_price = dp.precision_get('Product Price')
        prec_disc = dp.precision_get('Discount')
        prec_qty = dp.precision_get('Product Unit of Measure')

        if (inv_line.display_type or False) != (vals.get('display_type') or False):
            return False
        if (inv_line.name or '') != (vals.get('name') or ''):
            return False

        # Seção/nota: só nome e tipo importam
        if vals.get('display_type'):
            return True

        if inv_line.product_id.id != (vals.get('product_id') or False):
            return False
        if inv_line.product_uom_id.id != (vals.get('product_uom_id') or False):
            return False
        if float_compare(inv_line.quantity, vals.get('quantity', 0.0),
                         precision_digits=prec_qty):
            return False
        if float_compare(inv_line.price_unit, vals.get('price_unit', 0.0),
                         precision_digits=prec_price):
            return False
        if float_compare(inv_line.discount, vals.get('discount', 0.0),
                         precision_digits=prec_disc):
            return False

        tax_ids = set()
        for cmd in vals.get('tax_ids') or []:
            if cmd[0] == 6:
                tax_ids = set(cmd[2])
        if set(inv_line.tax_ids.ids) != tax_ids:
            return False

        if (inv_line.analytic_distribution or {}) != (vals.get('analytic_distribution') or {}):
            return False

        return True

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