# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import date, timedelta
from odoo.osv import expression
#from sshtunnel import SSHTunnelForwarder
# import odoorpc

# from odoo.addons.br_boleto.boleto.document import Boleto

class ContractContract(models.Model):
    _inherit = 'contract.contract'

    email_fat = {}

    def relatorio_contrato_erro(self):
        """
            -Vou buscar direto nos contratos os que foram faturados ou nao
            -pegar as faturas nao confirmadas
            -pegar faturas confirmadas sem boleto
            -pegar faturas confirmadas com boletos
            e exibir tudo em um email
        """
        email_line = {}
        email_rel = {}
        context = {}
        current_date =  time.strftime('%Y-%m-%d')
        if ids:
            contract_ids = ids
        else:
            contract_ids = self.search([
                ('recurring_next_date','<=', current_date),
                ('state','=', 'open'),
                ('recurring_invoices','=', True),
                ('type', '=', 'contract')])
        # CONTRATOS QUE NAO FORAM FATURADOS E PERMANECEM COM A MESMA DATA DE RECORRENCIA
        if contract_ids:
            #cr.execute('SELECT company_id, array_agg(id) as ids FROM account_analytic_account WHERE id IN %s\
            # GROUP BY company_id', (tuple(contract_ids),))
            #for company_id, ids in cr.fetchall():
            #for company_id, ids in contract_ids:
            #    d_val['empresa'] = company_id
            for contract in self.browse(contract_ids):
                #d_val['empresa'] = contract.company_id
                #d_val['contrato'] = contract
                #d_val['cliente'] = contract.partner_id
                context['empresa'] = contract.company_id
                context['cliente'] = contract.partner_id.id
                context['contrato'] = contract.code
                context['id_contrato'] = contract.id
                valido = self.validando_info(context)
                if len(valido):
                    email_line = {'faturado':'NAO',
                        'contrato': contract.code,
                        'cliente': contract.partner_id.name,
                        'ocorrencia': valido
                    }
                    email_dados = email_rel.setdefault(id,email_line)
                    email_retorno = email_dados.setdefault('NAO FATURADO', {})
                    continue
            if len(email_rel):
                #template_id =self.env['ir.model.data'].get_object_reference(cr,uid, 'seg_contract','email_erro_fatura')[1]
                ir_model_data = self.env['ir.model.data']
                try:
                    template_id = ir_model_data.get_object_reference('contract_billing', 'email_erro_fatura')[1]
                except ValueError:
                    template_id = False
                context['data'] = email_rel
                #self.pool.get('email.template').send_mail(cr, uid,template_id, uid, force_send=True, context=context)
                #self.env['email.template'].send_mail(
                #    self.env.cr, self.env.uid, template.id, self.id, force_send=True,
                #    context=context)
                self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)

    def relatorio_faturamento(self, faturado, id, contrato, cliente, ocorrencia, enviar, unidade):
        context = {}
        email_txt = {}
        if faturado == 'NAO':
            email_txt = {'faturado':'NAO',
                        'contrato': contrato,
                        'cliente': cliente,
                        'ocorrencia': ocorrencia,
                        'unidade': unidade
                    }
            email_data = self.email_fat.setdefault(id,email_txt)
            email_return = email_data.setdefault('NAO FATURADO', {})
        if faturado == 'SIM':
            email_txt = {'faturado':'SIM',
                        'contrato': contrato,
                        'cliente': cliente,
                        'ocorrencia': '',
                        'unidade': unidade
                    }
            email_data = self.email_fat.setdefault(id,email_txt)
            email_return = email_data.setdefault('FATURADO', {})
        if enviar == 'SIM':
            #template_id =self.pool.get('ir.model.data').get_object_reference(cr,uid, 'seg_contract','email_erro_fatura')[1]
            ir_model_data = self.env['ir.model.data']
            try:
                template_id = ir_model_data.get_object_reference('contract_billing', 'email_erro_fatura')[1]
            except ValueError:
                template_id = False
            context['data'] = self.email_fat.items()
            #self.pool.get('email.template').send_mail(cr, uid,template_id, uid, force_send=True, context=context)
            #self.env['email.template'].send_mail(
            #    self.env.cr, self.env.uid, template.id, self.id, force_send=True,
            #    context=context)
            self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)

    def validando_info(self, context=None):
        msg_inc = []
        if context:
            empresa = context.get('empresa')
            #cliente = context.get('cliente')
            contrato = context.get('contrato')
        msg_erro = ''
        # validando diario da empresa
        journal_obj = self.env['account.journal']
        journal_ids = journal_obj.search([('type', '=','sale')], limit=1)
        #,('company_id', '=', empresa.id or False)], limit=1)
        if not journal_ids:
            msg_inc.append({'cadastro': 'Sem Diário : %s' %(empresa.name)})
            msg_erro = 'Defina um diario para a empresa; %s.' %(empresa.name)
        # valida contrato (cliente, empresa, unidade, produto)
        if not contrato.partner_id:
            msg_inc.append({'cadastro': 'Contrato %s sem cliente definido.' % (contrato.name)})
            msg_erro = msg_erro + 'Contrato sem cliente definido; '
        else:
            cli = contrato.partner_id
            cli_name = cli.legal_name or cli.name
            # dados necessario para gerar o boleto
            #or not cli.number \  tirei pq na importacao foi no street
            if not cli.cnpj_cpf \
                    or not cli_name \
                    or not cli.zip \
                    or not cli.street \
                    or not cli.city_id \
                    or not cli.district \
                    or not cli.state_id \
                    or not cli.country_id:
                msg_erro = msg_erro + u'Falta CNPJ/CPF, Contratante, Endereco completo; '
            if not contrato.payment_term_id and not cli.property_payment_term_id:
                msg_erro = msg_erro + u'Falta Condicoes de Pagamento do Cliente; '
            # if not contrato.payment_mode_id:
            #     msg_erro = msg_erro + u'Falta Modo de Pagamento do Cliente; '
            #if not contrato.fiscal_position_id and not cli.property_account_position_id:
            #    msg_erro = msg_erro + u'Falta Posicao Fiscal; '

            #if empresa.id != cli.company_id.id:
            #    msg_erro = msg_erro + u'Empresa no contrato diferente do cadastro do cliente; '
            #if empresa.id != cli.property_account_receivable_id.company_id.id:
            #    msg_erro = msg_erro +  u'Conta de Recebimento nao pertence a empresa do contrato; '
            #if empresa.id != cli.property_account_position_id.company_id.id:
            #    msg_erro = msg_erro + u'Posicao Fiscal nao pertence a empresa do contrato; '
            if len(msg_erro):
                msg_inc.append({'cadastro': msg_erro}) # TODO estou repetindo as msg aqui tem q tirar
                if len(msg_inc):
                    contrato.message_post(body=_(msg_inc))
            # fatura invalida
            #venda = self.env['sale.order']
            #venda_cli = venda.search([('state', '=', 'sale'),('partner_id','=', cli.id)])
            #for sale_order in venda_cli:
            #    if sale_order.state != 'sale':
            #        msg_erro = msg_erro + 'Fatura com status diferente de Manual %s; ' %(sale_order.name)

        # validar informacoes no contrato
        #if empresa.id != contrato.company_id.id:
        #    msg_erro = msg_erro + u'Empresa diferente da Unidade no contrato; '

        return msg_erro

    def cron_gerar_boletos(self):
        data_fatura = date.today()
        data_fatura = data_fatura - timedelta(days=10)
        invoices = self.env['account.move'].search([
            ("payment_mode_id.payment_mode_domain", "=", "boleto"),
            ("state", "=", "posted"),
            ("invoice_date", ">", data_fatura)
        ])
        for invoice in invoices:            
            if invoice.amount_total > 0.01:
                if invoice.payment_mode_id.payment_mode_domain == "boleto":
                    if invoice.payment_mode_id.fixed_journal_id:
                        # se banco inter, a action abaixo faz o necessario
                        if invoice.payment_mode_id.fixed_journal_id.bank_id.code_bc == "077":
                            invoice.action_pdf_boleto()

    def _recurring_create_invoice(self, date_ref=False):
        # substitui tudo pra nao passar pelo l10n_br_contract
        # pois, temos contrato sem operacao
        invoices_values = self._prepare_recurring_invoices_values(date_ref)
        moves = self.env["account.move"].create(invoices_values)
        self._add_contract_origin(moves)
        self._invoice_followers(moves)
        self._compute_recurring_next_date()
        for move in moves:
            if move.fiscal_document_id:
                move.fiscal_document_id._onchange_document_serie_id()
                move.fiscal_document_id._onchange_company_id()
                move._onchange_invoice_line_ids()
            if move.amount_total > 0.01:
                move.action_post()
        return moves
    
    @api.model
    def _cron_recurring_create(self, date_ref=False, create_type="invoice"):
        """
        Faturo 30 contratos por vez
        """
        _recurring_create_func = self._get_recurring_create_func(
            create_type=create_type
        )
        if not date_ref:
            date_ref = fields.Date.context_today(self)
        domain = self._get_contracts_to_invoice_domain(date_ref)
        domain = expression.AND(
            [
                domain,
                [("generation_type", "=", create_type)],
            ]
        )
        contracts = self.search(domain)
        companies = set(contracts.mapped("company_id"))
        # contract_invoice
        # Invoice by companies, so assignation emails get correct context
        for company in companies:
            contracts_to_invoice = contracts.filtered(
                lambda c: c.company_id == company
                and (not c.date_end or c.recurring_next_date <= c.date_end)
            ).with_company(company)
            for ctr in contracts_to_invoice[:30]:
                if ctr.fiscal_operation_id:
                    for line in ctr.contract_line_ids:
                        if not line.fiscal_operation_line_id:
                            msg = f"Contrato {ctr.code}:{ctr.name} com linha {line.name} sem Operação Fiscal."
                            canal = self.env['mail.channel'].search([('name', '=', 'geral')], limit=1)
                            canal.message_post(
                                body=(msg),
                                message_type='comment',
                                subtype_xmlid='mail.mt_comment',
                            )
                            continue
                _recurring_create_func(ctr, date_ref)
        return True