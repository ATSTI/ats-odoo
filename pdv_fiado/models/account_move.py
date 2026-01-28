from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create_fiado_from_pos(self, partner_id, order_lines, amount_paid):
        """
        Cria uma fatura tipo 'fiado' a partir do POS.
        NÃO emite NFe nem tenta validar o pagamento.
        Apenas cria a fatura com as linhas e o parceiro.
        """
        # Prepara as linhas da fatura
        move_lines = []
        for line in order_lines: #pra cada linha
            move_lines.append((0, 0, {
                'product_id': line['product_id'], #produto
                'quantity': line['quantity'], #quantidade
                'price_unit': line['price_unit'],# preco unitario
                'tax_ids': [(6, 0, line['tax_ids'])], #impostos
            }))

        # Cria a fatura
        move = self.env['account.move'].create({
            'move_type': 'out_invoice',  # fatura de cliente
            'partner_id': partner_id,
            'invoice_line_ids': move_lines,
        })
        move.action_post()

        return {
            'id': move.id,
            'name': move.name,
            'total': sum([l['price_unit']*l['quantity'] for l in order_lines]),
        }
