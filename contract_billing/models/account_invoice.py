# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    email_send = fields.Boolean(string="Email enviado")

    move_tag_ids = fields.Many2many(comodel_name="contract.tag", string="Marcadores")


    # Campo relacionado ao website do parceiro, armazenado no banco e somente leitura.
    partner_website = fields.Char(
        string="Website do Cliente",
        related="partner_id.website",
        store=True,
        readonly=True,
        help="Espelha o campo Website do parceiro e persiste no registro da fatura."
    )

    #FATURAMENTO PRODUTORES
    def _get_billing_producer_domain(self):
        sale_model = self.env['sale.order']
        invoice_model = self.env['account.move']
        log_model = self.env['ir.logging']

        multiplicadores = {
            3: 50,
            4: 60,
        }

        quotations = sale_model.search([
            ('state', '=', 'draft'),
            ('create_date', '>=', '2025-07-01 00:00:00')
        ],limit=50)
        invoices = invoice_model.search([
            ('state', '=', 'draft'),
            ('move_type', '=', 'out_invoice')
        ],limit=50)

        quotes_by_partner = {}
        for quote in quotations:
            pid = quote.partner_id.id
            quotes_by_partner.setdefault(pid, []).append(quote)

        invoices_by_partner = {}
        for inv in invoices:
            pid = inv.partner_id.id
            invoices_by_partner.setdefault(pid, []).append(inv)

        common_partner_ids = set(quotes_by_partner.keys()) & set(invoices_by_partner.keys())

        for pid in common_partner_ids:
            for quote in quotes_by_partner[pid]:
                try:
                    quote.action_confirm()
                    log_model.create({
                        'name': 'Cron',
                        'type': 'server',
                        'level': 'info',
                        'message': 'Cotação confirmada: ' + quote.name,
                        'path': 'action_server',
                        'func': 'cron',
                        'line': 0,
                    })
                except Exception as e:
                    log_model.create({
                        'name': 'Cron',
                        'type': 'server',
                        'level': 'error',
                        'message': 'Erro ao confirmar cotação ' + quote.name + ': ' + str(e),
                        'path': 'action_server',
                        'func': 'cron',
                        'line': 0,
                    })

            for inv in invoices_by_partner[pid]:
                try:
                    sale = sale_model.search([
                        ('partner_id', '=', pid),
                        ('state', '=', 'sale'),
                        ('create_date', '>=', '2025-07-01 00:00:00')
                    ], limit=1)

                    if sale:
                        total_venda = sale.amount_total
                        multiplicador = 1

                        tag_ids = [tag.id for tag in inv.move_tag_ids]
                        if 2 in tag_ids:
                            if total_venda == 1:
                                multiplicador = 90
                            elif total_venda in [2, 3, 4, 5]:
                                multiplicador = 70
                            else:
                                multiplicador = 60
                        else:
                            for tag_id in tag_ids:
                                if tag_id in multiplicadores:
                                    multiplicador = multiplicadores[tag_id]
                                    break

                        total_ajustado = total_venda * multiplicador

                        if not inv.invoice_line_ids:
                            raise ValueError('Fatura sem linhas para basear o produto.')

                        produto = inv.invoice_line_ids[0].product_id
                        conta = inv.invoice_line_ids[0].account_id

                        if not produto or not conta:
                            raise ValueError('Produto ou conta da linha original não encontrada.')

                        inv.write({'invoice_line_ids': [(5, 0, 0)]})
                        inv.write({
                            'invoice_line_ids': [(0, 0, {
                                'move_id': inv.id,
                                'product_id': produto.id,
                                'name': produto.name,
                                'quantity': 1,
                                'price_unit': total_ajustado,
                                'account_id': conta.id,
                            })]
                        })
                        inv._compute_amount()
                        inv.with_context(check_move_validity=False).action_post()

                    status_final = inv.state
                    log_model.create({
                        'name': 'Cron',
                        'type': 'server',
                        'level': 'info',
                        'message': 'Fatura ' + inv.name + ' finalizada com status: ' + status_final + ' (mult.=' + str(multiplicador) + ')',
                        'path': 'action_server',
                        'func': 'cron',
                        'line': 0,
                    })

                except Exception as e:
                    log_model.create({
                        'name': 'Cron',
                        'type': 'server',
                        'level': 'error',
                        'message': 'Erro ao ajustar ou confirmar fatura ' + inv.name + ': ' + str(e),
                        'path': 'action_server',
                        'func': 'cron',
                        'line': 0,
                    })
