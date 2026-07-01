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
        msg_log = ''
        for sale in quotations:
            try:
                sale.action_confirm()
                msg_log += 'Confirmada: %s-%s' %(sale.name, sale.partner_id.name[:20])
            except Exception as e:
                log_model.create({
                    'name': 'Cron',
                    'type': 'server',
                    'level': 'error',
                    'message': 'Erro ao confirmar cotação ' + sale.name + ': ' + str(e),
                    'path': 'action_server',
                    'func': 'cron',
                    'line': 0,
                })
            inv = invoice_model.search([
                ('state', '=', 'draft'),
                ('move_type', '=', 'out_invoice'),
                ('partner_id', '=', sale.partner_id.id)
            ],limit=1)

            if not inv:
                log_model.create({
                    'name': 'Cron',
                    'type': 'server',
                    'level': 'error',
                    'message': 'Erro: SEM Fatura para cliente : ' + sale.partner_id.name,
                    'path': 'action_server',
                    'func': 'cron',
                    'line': 0,
                })
                continue

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
                log_model.create({
                    'name': 'Cron',
                    'type': 'server',
                    'level': 'error',
                    'message': f"Erro sem linha de produto fatura (ID:{inv.id}: {sale.partner_id.name}",
                    'path': 'action_server',
                    'func': 'cron',
                    'line': 0,
                })
            try:
                for line in inv.invoice_line_ids:
                    line.write({                       
                        'price_unit': total_ajustado,
                    })
                inv._compute_amount()
                inv.with_context(check_move_validity=False).action_post()
                status_final = inv.state
                msg_log += ' | Fatura: %s - %s (mult.=%s) \n' %(inv.name, status_final, str(multiplicador))
            except Exception as e:
                log_model.create({
                    'name': 'Cron',
                    'type': 'server',
                    'level': 'error',
                    'message': f"Erro ao ajustar ou confirmar fatura (ID:{inv.id}): {str(e)}",
                    'path': 'action_server',
                    'func': 'cron',
                    'line': 0,
                })
        if msg_log:
            log_model.create({
                'name': 'Cron',
                'type': 'server',
                'level': 'info',
                'message': msg_log,
                'path': 'action_server',
                'func': 'cron',
                'line': 0,
            })
