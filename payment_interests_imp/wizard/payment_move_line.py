# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import date

class AccountPayment(models.Model):
    _inherit = "account.payment"

    juros = fields.Monetary(
        string='Juros', readonly=True)
    multa = fields.Monetary(
        string='Multa', readonly=True)
    valor_original = fields.Monetary(
        string='Vlr. Original', readonly=True)
    incluir_juros = fields.Boolean(string="Incluir Juros/Multa")
 
    @api.model
    def default_get(self, fields):
        if 'move_line_id' in fields:
            rec = super(AccountPayment, self).default_get(fields)
        else:
            return super(AccountPayment, self).default_get(fields)
        move_line_id = rec.get('move_line_id', False)
        move_line = self.env['account.move.line'].browse(move_line_id)
        current_date = date.today()
        cpn = self.env['res.company.interest'].browse(move_line.company_id.id)
        data_vcto = current_date
        if move_line.date_maturity:
            data_vcto = move_line.date_maturity
        quantidade_dias = abs((current_date - data_vcto).days)
        if quantidade_dias < cpn.tolerance_interval:
            return rec
        quantidade_dias = quantidade_dias - cpn.tolerance_interval
        multa = move_line.debit * (cpn.multa/100)
        juros = cpn.company_id.currency_id.round(
            (cpn.rate/100) * quantidade_dias * move_line.debit)
        rec.update({
            'multa': multa,
            'juros': juros,
            'valor_original': move_line.debit,
        })

        return rec

    @api.onchange('incluir_juros')
    def _onchange_incluir_juros(self):
        if self.incluir_juros:
            self.amount = self.amount + self.juros + self.multa
        if not self.incluir_juros and self.amount > self.valor_original:
            self.amount = self.valor_original


class PaymentAccountMoveLine(models.TransientModel):
    _inherit = 'payment.account.move.line'
 
    @api.depends('amount', 'payment_date', 'currency_id', 'valor_original')
    def _compute_payment_difference(self):
        if self.valor_original > 0 and self.amount > self.valor_original:
            self.payment_difference = self.amount - self.valor_original
    
    juros = fields.Monetary(
        string='Juros', readonly=True)
    multa = fields.Monetary(
        string='Multa', readonly=True)
    valor_original = fields.Monetary(
        string='Vlr. Original', readonly=True)
    incluir_juros = fields.Boolean(string="Incluir Juros/Multa")
    payment_difference = fields.Monetary(compute='_compute_payment_difference', readonly=True)
    writeoff_account_id = fields.Many2one('account.account', string="Conta Diferença", domain=[('deprecated', '=', False)], copy=False) 
    writeoff_label = fields.Char(
        string='Journal Item Label',
        default='')
 
    @api.model
    def default_get(self, fields):
        if 'move_line_id' in fields:
            rec = super(PaymentAccountMoveLine, self).default_get(fields)
        else:
            return super(AccountPayment, self).default_get(fields)
        move_line_id = rec.get('move_line_id', False)
        move_line = self.env['account.move.line'].browse(move_line_id)
        current_date = date.today()
        cpn = self.env['res.company.interest'].search([('company_id','=',move_line.company_id.id)])
        if move_line.debit > 0:
            rec.update({'valor_original': move_line.debit})
        if move_line.credit > 0:
            rec.update({'valor_original': move_line.credit})
        if move_line.date_maturity >= current_date:
            rec.update({'valor_original': move_line.debit})
            return rec
        quantidade_dias = abs((current_date - move_line.date_maturity).days)
        if cpn.tolerance_interval:
            if quantidade_dias < cpn.tolerance_interval:
                rec.update({'valor_original': move_line.debit})
                return rec
            quantidade_dias = quantidade_dias - cpn.tolerance_interval
            multa = move_line.debit * (cpn.multa/100)
            juros = cpn.company_id.currency_id.round(
                (cpn.rate/100) * quantidade_dias * move_line.debit)
            rec.update({
                'multa': multa,
                'juros': juros,
                'valor_original': move_line.debit,
            })
        
        return rec

    @api.onchange('incluir_juros')
    def _onchange_incluir_juros(self):
        if self.incluir_juros:
            self.amount = self.amount + self.juros + self.multa
            self.payment_difference = self.amount - self.valor_original
        if not self.incluir_juros and self.amount > self.valor_original:
            self.amount = self.valor_original

    def _get_payment_vals(self):
        """
        Method responsible for generating payment record amounts
        """
        payment_type = 'inbound' if self.move_line_id.debit else 'outbound'
        payment_methods = \
            payment_type == 'inbound' and \
            self.journal_id.inbound_payment_method_ids or \
            self.journal_id.outbound_payment_method_ids
        payment_method_id = payment_methods and payment_methods[0] or False
        vals = {
            'partner_id': self.partner_id.id,
            'move_line_id': self.move_line_id.id,
            'journal_id': self.journal_id.id,
            'communication': self.communication,
            'amount': self.amount,
            'payment_date': self.payment_date,
            'payment_type': payment_type,
            'payment_method_id': payment_method_id.id,
            'currency_id': self.currency_id.id,
            'payment_difference': self.payment_difference,
            'writeoff_account_id': self.writeoff_account_id.id,
        }
        return vals

    """
    @api.multi
    def post(self, payment):
        for rec in payment:

            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be posted."))

            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            # keep the name in case of a payment reset to draft
            if not rec.name:
                # Use the right sequence to set the name
                if rec.payment_type == 'transfer':
                    sequence_code = 'account.payment.transfer'
                else:
                    if rec.partner_type == 'customer':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.customer.invoice'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.customer.refund'
                    if rec.partner_type == 'supplier':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.supplier.refund'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.supplier.invoice'
                rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
                if not rec.name and rec.payment_type != 'transfer':
                    raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

            # Create the journal entry
            amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            move = self._create_payment_entry(payment, amount)
            persist_move_name = move.name

            # In case of a transfer, the first journal entry created debited the source liquidity account and credited
            # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
            if rec.payment_type == 'transfer':
                transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
                transfer_debit_aml = self._create_transfer_entry(payment, amount)
                (transfer_credit_aml + transfer_debit_aml).reconcile()
                persist_move_name += payment._get_move_name_transfer_separator() + transfer_debit_aml.move_id.name

            rec.write({'state': 'posted', 'move_name': persist_move_name})
        return True
    """
    """
    def _create_payment_entry(self, payment, amount):
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=payment.payment_date)._compute_amount_fields(amount, payment.currency_id, payment.company_id.currency_id)

        move = self.env['account.move'].create(payment._get_move_vals())

        #Write line corresponding to invoice payment
        
        counterpart_aml_dict = payment._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
        counterpart_aml_dict.update(payment._get_counterpart_move_line_vals(payment.invoice_ids))
        counterpart_aml_dict.update({'currency_id': currency_id})
        counterpart_aml = aml_obj.create(counterpart_aml_dict)

        #Reconcile with the invoices
        if payment.payment_difference_handling == 'reconcile' and payment.payment_difference:
            writeoff_line = payment._get_shared_move_line_vals(0, 0, 0, move.id, False)
            debit_wo, credit_wo, amount_currency_wo, currency_id = aml_obj.with_context(date=payment.payment_date)._compute_amount_fields(payment.payment_difference, payment.currency_id, payment.company_id.currency_id)
            writeoff_line['name'] = payment.writeoff_label
            writeoff_line['account_id'] = payment.writeoff_account_id.id
            writeoff_line['debit'] = debit_wo
            writeoff_line['credit'] = credit_wo
            writeoff_line['amount_currency'] = amount_currency_wo
            writeoff_line['currency_id'] = currency_id
            writeoff_line = aml_obj.create(writeoff_line)
            if counterpart_aml['debit'] or (writeoff_line['credit'] and not counterpart_aml['credit']):
                counterpart_aml['debit'] += credit_wo - debit_wo
            if counterpart_aml['credit'] or (writeoff_line['debit'] and not counterpart_aml['debit']):
                if self.valor_original < self.amount:
                    counterpart_aml['credit'] = self.amount - self.valor_original
                #counterpart_aml['credit'] += debit_wo - credit_wo
            counterpart_aml['amount_currency'] -= amount_currency_wo

        #Write counterpart lines
        if not payment.currency_id.is_zero(payment.amount):
            if not payment.currency_id != payment.company_id.currency_id:
                amount_currency = 0
            liquidity_aml_dict = payment._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
            liquidity_aml_dict.update(payment._get_liquidity_move_line_vals(-amount))
            aml_obj.create(liquidity_aml_dict)

        #validate the payment
        if not payment.journal_id.post_at_bank_rec:
            move.post()

        #reconcile the invoice receivable/payable line(s) with the payment
        if payment.invoice_ids:
            payment.invoice_ids.register_payment(counterpart_aml)

        return move
    """

    def inv_line_characteristic_hashcode(self, invoice_line):
        """Overridable hashcode generation for invoice lines. Lines having the same hashcode
        will be grouped together if the journal has the 'group line' option. Of course a module
        can add fields to invoice lines that would need to be tested too before merging lines
        or not."""
        return "%s-%s-%s-%s-%s-%s-%s" % (
            invoice_line['account_id'],
            invoice_line.get('tax_ids', 'False'),
            invoice_line.get('tax_line_id', 'False'),
            invoice_line.get('product_id', 'False'),
            invoice_line.get('analytic_account_id', 'False'),
            invoice_line.get('date_maturity', 'False'),
            invoice_line.get('analytic_tag_ids', 'False'),
        )
        
    # CRIO UM MOVIMENTO COM O JUROS 
    @api.multi
    def action_move_create_interests(self, values):
        """ Creates invoice related analytics and financial move lines """
        account_move = self.env['account.move']
        
        move_vals = {
            'ref': values['ref'],
            'journal_id': values['journal_id'],
            'date': values['date'],
            'narration': 'Juros Recebidos',
            'line_ids': [
                (0, 0, {'debit': values['payment_difference'], 
                        'account_id': values['account_id'],
                        'journal_id': values['journal_id'],
                        'ref': values['ref'],
                        'name': values['name'],
                        'invoice_id': values['invoice_id'],
                        'partner_id': values['partner_id'],
                        }),
                (0, 0, {'credit': values['payment_difference'], 
                        'account_id': values['writeoff_account_id'],
                        'ref': values['ref'],
                        'name': values['name'],
                        'journal_id': values['journal_id'],
                        'invoice_id': values['invoice_id'],
                        'partner_id': values['partner_id'],
                        }),
            ],
        }
        move = account_move.create(move_vals)
        move.action_post()
        #move.line_ids.reconcile()
        return move

    def action_confirm_payment(self):
        """
        Method responsible for creating the payment
        """
        payment = self.env['account.payment']
        vals = self._get_payment_vals()
        move_line = self.env['account.move.line'].browse(vals['move_line_id'])
        if vals['payment_difference'] > 0:
            vls_juros = vals
            vls_juros['amount'] = vls_juros['amount'] - vals['payment_difference']
            vls_juros['account_id'] = self.journal_id.default_debit_account_id.id
            vls_juros['writeoff_account_id'] = vals['writeoff_account_id']
            vls_juros['move_id'] = move_line.move_id.id
            if self.writeoff_label:
                vls_juros['name'] = self.writeoff_label
            else:
                vls_juros['name'] = 'Juros Recebidos - %s' %(move_line.partner_id.name)
            vls_juros['ref'] = move_line.id
            vls_juros['debit'] = vals['payment_difference']
            vls_juros['date'] = vals['payment_date']
            vls_juros['invoice_id'] = move_line.invoice_id.id,
            vls_juros['partner_id'] = move_line.partner_id.id,
            # vou criar um lançamento na account.move.line do juros
            self.action_move_create_interests(vls_juros)

        pay = payment.with_context(
            force_counterpart_account=self.move_line_id.account_id.id).\
            create(vals)
        pay.post()
                
        lines_to_reconcile = (pay.move_line_ids + move_line).filtered(
            lambda l: l.account_id == move_line.account_id)
        lines_to_reconcile.reconcile()

        aml_obj = self.env['account.move.line'].\
            with_context(check_move_validity=False)
        return self.env.ref('payment_interests.report_invoice_cupom').report_action(self)
