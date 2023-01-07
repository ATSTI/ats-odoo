# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import time
from datetime import datetime
import base64

from odoo.addons.br_boleto.boleto.document import Boleto

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

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



    #def relatorio_faturamento(self, faturado, id, contrato, cliente, ocorrencia, enviar, unidade):
    def relatorio_faturamento(self):
        # vou gerar um relatorio analisando todos os contratos nao faturados
        context = {}
        contracts = self.search([
            ('recurring_next_date', '<=', fields.date.today()),
            ('recurring_invoices', '=', True),
            ('active','=',True)])
        corpo = "<table border='1' cellspacing='0' cellpadding='2' width='100%'>"
        corpo += "<caption>Contratos não faturados</caption>"
        corpo += "<tr>"
        corpo += "<th width='20%'>Contrato</th>"
        corpo += "<th width='30%'>Cliente</th>"
        corpo += "<th width='50%'>Motivo</th>"
        corpo += "</tr>"
        for ctr in contracts:
            corpo += "<tr>"
            corpo += "<td>%s</td>" %(ctr.name)
            corpo += "<td>%s</td>" %(ctr.partner_id.name)
            corpo += "<td>%s</td>" %(ctr.msg_faturamento)
            corpo += "</tr>"
        corpo += "</table>"
    
        # enviando email res.partner = 1
        assunto = 'Relatorio de Erros no Faturamento - %s/%s/%s' %(
            str(fields.date.today().day).zfill(2),
            str(fields.date.today().month).zfill(2),
            str(fields.date.today().year))
        mail_details = {'subject': assunto,
            'body': corpo,
            'partner_ids': [(1)]
            } 
        mail = self.env['mail.thread']
        mail.message_post(type="notification", subtype="mt_comment", **mail_details)

            
        """
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
        """

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
            if not cli.cnpj_cpf:
                msg_erro = msg_erro + u'Falta CNPJ/CPF; '
            if not cli.zip:
                msg_erro = msg_erro + u'Faltando CEP; '
            if not cli.street:
                msg_erro = msg_erro + u'Rua não informada; '
            if not cli.city_id:
                msg_erro = msg_erro + u'Cidade não informada; '
            if not cli.district:
                msg_erro = msg_erro + u'Bairro não informado; '
            if not cli.state_id:
                msg_erro = msg_erro + u'Estado(UF) não informado; '
            if not cli.country_id:
                msg_erro = msg_erro + u'País não informado; '
            if not cli.number:
                msg_erro = msg_erro + u'Faltando Número no endereco; '
            if not contrato.payment_term_id and not cli.property_payment_term_id:
                msg_erro = msg_erro + u'Falta Condicoes de Pagamento do Cliente; '
            if not contrato.payment_mode_id and not cli.payment_mode_id:
                msg_erro = msg_erro + u'Falta Modo de Pagamento do Cliente; '
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

        return msg_erro

    """ 5 - Gerando o boleto """
    def criar_boleto(self, invoice, move):
        invoice_ids = self.env['account.invoice'].browse([invoice])
        self.env['payment.order.line'].action_register_boleto(
            invoice_ids.receivable_move_line_ids)
        #boleto_list = move.action_register_boleto()

        boleto_nome = '%s%s%s-%s.pdf' %(
                    str(move.date.day).zfill(2),
                    str(move.date.month).zfill(2),
                    str(move.date.year),
                    move.move_id.name
                )
        item = move.invoice_id
        
        boleto_report = self.env['ir.actions.report'].search(
              [('report_name', '=',
              'br_boleto.report.print')])
        report_service = boleto_report.xml_id
        boleto, dummy = self.env.ref(report_service).render_qweb_pdf(
                [item.id])

        if boleto:
            name = "boleto-%s-%s.pdf" % (
               item.number, item.partner_id.commercial_partner_id.name)
            attachment_obj = self.env['ir.attachment']
            boleto_id = attachment_obj.create(dict(
                    name=name,
                    datas_fname=name,
                    datas=base64.b64encode(boleto),
                    mimetype='application/pdf',
                    res_model='account.invoice',
                    res_id=item.id,
                ))
        return boleto

    """ 3 - Executa o faturamento das vendas existentes """
    def faturar_invoice(self):
        #venda = self.env['sale.order']
        #venda_ids = venda.search([
        #    ('partner_id','=',self.partner_id.id),
        #    ('state', '=', 'sale'),
        #    ('invoice_status', '=', 'to invoice')
        #])
        mes_ant = '%s-%s-01 01:00:00' %(fields.date.today().year, fields.date.today().month)
        venda = self.env['sale.order']
        venda_ids = venda.search([
            ('partner_id','=', self.partner_id.id),
            ('state', '=', 'sale'),
            ('confirmation_date','>', mes_ant),
            ('invoice_status', '=', 'to invoice')])
        id = venda_ids.action_invoice_create()
        return id

    @api.multi
    def _create_invoice(self):
        invoice_ids = []
        invoice_vals = self._prepare_invoice()
        msg_erro = ''
        #try:
        if msg_erro == '':
            msg_erro = 'Erro para criar Pedido Venda.'
            invoice_vals['partner_shipping_id'] = invoice_vals['partner_id']
            invoice_ids.append(self.env['sale.order'].create(invoice_vals))
            #invoice = self.env['account.invoice'].create(invoice_vals)
            msg_erro = 'Erro para adicionar itens pedido de venda.'
            self._prepare_order_lines(self, invoice_ids[0])
            msg_erro = 'Erro pra confirmar pedido de venda.'
            invoice_ids[0].action_confirm()
            msg_erro = 'Erro para criar a Fatura.'
            inv_id = self.faturar_invoice()
            invoice = self.env['account.invoice'].browse(inv_id)
            if not invoice.payment_mode_id:
                pay = {}
                if self.payment_mode_id:
                    pay['payment_mode_id'] = self.payment_mode_id.id
                    invoice.write(pay)
            msg_erro = 'Erro para Confirmar a Fatura.'
            invoice.action_invoice_open()
            if invoice.payment_mode_id.boleto_type:
                msg_erro = 'Erro para Gerar o Boleto.'
                self.criar_boleto(invoice.id, invoice.receivable_move_line_ids[0])
            msg_erro = ''
            #self.relatorio_faturamento('SIM', self.id, self.code, self.partner_id.name, '',
            #    'NAO', self.company_id.name)
            return invoice, msg_erro
        #except Exception:
        #    self.env.cr.rollback()
        #    return False, msg_erro

    @api.multi
    def _prepare_invoice_proprietario(self, proprietario, data_fatura=None):
        self.ensure_one()
        currency = (
            proprietario.partner_id.property_product_pricelist.currency_id or
            self.company_id.currency_id
        )
        invoice_type = 'in_invoice'
        payment_term_id = 1
        if proprietario.payment_term_id:
            payment_term_id = proprietario.payment_term_id.id
        fiscal_position_id = 2 # Pagamentos
        if not data_fatura:
            data_fatura = self.recurring_next_date
        else:
            data_fatura = datetime.strptime(data_fatura, '%Y-%m-%d')
        tempo = str(self.tempo(self.mes_contrato, self.ano_contrato))
        reference = '%s(%s)-%s-%s' %(
            self.name, tempo, 
            str(data_fatura.month).zfill(2),
            data_fatura.year)
        journal = self.env['account.journal'].search([
                ('type', '=', 'purchase'),
                ('company_id', '=', self.company_id.id)
            ], limit=1)
        invoice = self.env['account.invoice'].new({
            'payment_term_id': payment_term_id,
            'fiscal_position_id': fiscal_position_id,
            'reference': reference,
            'type': invoice_type,
            'partner_id': proprietario.partner_id.address_get(
                ['invoice'])['invoice'],
            'currency_id': currency.id,
            'journal_id': journal.id,
            'date_invoice': data_fatura.strftime('%Y-%m-%d'),
            'origin': self.name,
            'company_id': self.company_id.id,
            'contract_id': self.id,
            'user_id': proprietario.partner_id.user_id.id,
        })
        # Get other invoice values from partner onchange
        invoice._onchange_partner_id()
        if not invoice.payment_term_id:
            invoice.payment_term_id = payment_term_id
        if not invoice.fiscal_position_id:
            invoice.fiscal_position_id = fiscal_position_id
        return invoice._convert_to_write(invoice._cache)
        

    def _prepare_order_lines_prop(self, contract, order_id, proprietario):
        invoice_lines = []
        for line in contract.recurring_invoice_line_ids:
            invoice_lines = []
            #if line.date_start and line.date_stop:
            #    if line.date_start <= self.recurring_next_date and line.date_stop > self.recurring_next_date:
            
            percent = 10
            if proprietario.percentual_aluguel:
                percent = proprietario.percentual_aluguel/100
            cota = 1
            if proprietario.cota:
                cota = proprietario.cota/100
            vlr = line.price_unit * line.quantity
            # ITEM ALUGUEL reduz comissao
            if line.product_id.id == 1:
                vlr = ((line.price_unit * line.quantity) *
                    ((1-percent) * cota))
            if line.repassa_prop:
                invoice_lines = {
                        'invoice_id': order_id.id,
                        'name': line.name,
                        'price_unit': vlr,
                        'uom_id': 1,
                        'quantity': 1,
                        'account_analytic_id': contract.id,
                        'product_id': line.product_id.id or False,
                        'account_id': line.product_id.categ_id.property_account_expense_categ_id.id
                }
            if len(invoice_lines):
                self.env['account.invoice.line'].create(invoice_lines)
        return invoice_lines

    @api.multi
    def _create_invoice_proprietario(self, proprietario, data_fatura=None):
        # verificando se existe linha marcada como repasse
        tem_repasse = False
        for line in self.recurring_invoice_line_ids:
            if line.repassa_prop:
                tem_repasse = True
        msg_erro = ''
        if not tem_repasse:
            return False, msg_erro
        """ GERANDO O CONTAS A PAGAR """
        invoice_vals = self._prepare_invoice_proprietario(proprietario, data_fatura)
        try:
            msg_erro = 'Erro para criar a fatura do Proprietario.'
            invoice = self.env['account.invoice'].create(invoice_vals)
            msg_erro = 'Erro para adicionar itens na fatura Proprietario.'
            self._prepare_order_lines_prop(self, invoice, proprietario)
            msg_erro = 'Erro pra confirmar a fatura Proprietario.'
            invoice.action_invoice_open()
            msg_erro = ''
            return invoice, msg_erro
        except Exception:
            #self.env.cr.rollback()
            return False, msg_erro

    @api.multi
    def recurring_create_invoice(self):
        context = {}
        email_line = {}
        email_rel = {}
        for contract in self:
            if not contract.active:
                continue
            if not contract.partner_id.active:
                continue
            context['cliente'] = contract.partner_id
            context['contrato'] = contract
            #context['empresa'] = contract.company_id
            context['id_contrato'] = contract.id
            valido = self.validando_info(context)
            if len(valido):
                contract.msg_faturamento = valido
                email_line = {'faturado':'NAO',
                    'contrato': contract.code,
                    'cliente': contract.partner_id.name,
                    'ocorrencia': valido
                }
                email_dados = email_rel.setdefault(id,email_line)
                email_dados.setdefault('NAO FATURADO', {})
                contract.message_post(body=_(email_dados))
                continue

            old_date = fields.Date.from_string(
                contract.recurring_next_date or fields.Date.today())
            new_date = old_date + self.get_relative_delta(
                contract.recurring_rule_type, contract.recurring_interval)
            ctx = self.env.context.copy()
            ctx.update({
                'old_date': old_date,
                'next_date': new_date,
                # Force company for correct evaluate domain access rules
                #'force_company': contract.company_id.id,
            })
            # Re-read contract with correct company
            contract.msg_faturamento = 'Faturado'
            try:
                inv, msg = contract.with_context(ctx)._create_invoice()
                if msg:
                    contract.msg_faturamento = msg
                for prop in contract.imovel_id.owner_ids:
                    if prop.partner_id:
                        msg_prop = contract.with_context(ctx)._create_invoice_proprietario(prop)
                        if msg_prop[1]:
                            contract.msg_faturamento = msg + msg_prop[1]
                if inv:
                    contract.write({
                        'recurring_next_date': new_date.strftime('%Y-%m-%d')
                    })
                    #self.env.cr.commit()
                else:
                    msg = 'Erro no faturamento,  ' + msg
                    contract.message_post(body=_(msg))
                    contract.msg_faturamento = msg
                    #self.relatorio_faturamento('NAO', contract.id, contract.code, contract.partner_id.name,
                #   'Erro ao executar o faturamento.', 'NAO', contract.company_id.name)
            except:
                continue
        #if len(email_rel):
        #    ir_model_data = self.env['ir.model.data']
        #    try:
        #        template_id = ir_model_data.get_object_reference('contract_billing', 'email_erro_fatura')[1]
        #    except ValueError:
        #        template_id = False
        #    context['data'] = email_rel
        #    #self.env['mail.template'].browse(template_id).send_mail(contract.id, force_send=True)
        #self.relatorio_faturamento()
        return True

    @api.model
    def cron_recurring_create_proprietario(self, data_next, data_fatura, venc_ini, venc_fim, id_ini):
        contracts = self.search(
            [('recurring_next_date', '<', data_next),
             ('recurring_invoices', '=', True),
             ('active','=',True),
             ('id', '>', id_ini),
             ('id', '<', id_ini+650),
             ('date_end', '>', venc_ini),
             ], order = 'name')
        contratos = []
        for ctr in contracts:
            contratos.append(ctr.name)
        inv = self.env['account.invoice'].search([
                    ('date_due', '>=', venc_ini),
                    ('date_due', '<=', venc_fim),
                    ('journal_id', '=', 2),
        ], order='origin')
        faturados = []
        for fatura in inv:
            faturados.append(str(fatura.origin)) 
        
        #import pudb;pu.db
        nao_faturado = list(set(contratos) - set(faturados))    
       
        contracts = self.search([
            ('name', 'in', nao_faturado)])
        for ctr in contracts:
            for prop in ctr.imovel_id.owner_ids:
                if prop.partner_id:
                    tempo = str(self.tempo(ctr.mes_contrato, ctr.ano_contrato))
                    data_f = datetime.strptime(data_fatura, '%Y-%m-%d')
                    reference = '%s(%s)-%s-%s' %(
                        ctr.name, tempo, 
                        str(data_f.month).zfill(2),
                        data_f.year)
                    # verifica se ja foi criado fatura pra este vencimento
                    inv = self.env['account.invoice'].search([
                    ('partner_id', '=', prop.partner_id.id),
                    ('date_invoice', '=', data_fatura),
                    ('reference', '=', reference),
                    ])
                    if not inv:
                        ctr._create_invoice_proprietario(prop, data_fatura)
        return True

    @api.model
    def cron_recurring_create_invoice(self):
        venc_ini = fields.date.today()
        # TODO 08/06/2022 acrescentei o venc_ini aqui verificar
        contracts = self.search(
            [('recurring_next_date', '<=', fields.date.today()),
             ('recurring_invoices', '=', True),
             ('date_end', '>', venc_ini),
             ('active','=',True)],limit=10)
        return contracts.recurring_create_invoice()

    def _prepare_order_lines(self, contract, order_id):
        invoice_lines = []
        for line in contract.recurring_invoice_line_ids:
            invoice_lines = []
            #if line.date_start and line.date_stop:
            #    if line.date_start <= self.recurring_next_date and line.date_stop > self.recurring_next_date:
            invoice_lines = {
                        'order_id': order_id.id,
                        'name': line.name,
                        'price_unit': line.price_unit or 0.0,
                        'product_uom_qty': line.quantity,
                        'product_id': line.product_id.id or False,
            }
            #'account_id': line.product_id.categ_id.property_account_income_categ_id.id
            """
            elif line.date_start and not line.date_stop:
                if line.date_start <= self.recurring_next_date:
                    invoice_lines = {
                        'order_id': order_id.id,
                        'name': line.name,
                        'price_unit': line.price_unit or 0.0,
                        'product_uom_qty': line.quantity,
                        'product_id': line.product_id.id or False,
                    }
            elif not line.date_start and line.date_stop:
                if line.date_stop > self.recurring_next_date:
                    invoice_lines = {
                        'order_id': order_id.id,
                        'name': line.name,
                        'price_unit': line.price_unit or 0.0,
                        'product_uom_qty': line.quantity,
                        'product_id': line.product_id.id or False,
                    }
            else:
                invoice_lines = {
                    'order_id': order_id.id,
                    'name': line.name,
                    'price_unit': line.price_unit or 0.0,
                    'product_uom_qty': line.quantity,
                    'product_id': line.product_id.id or False,
                }
            """
            if len(invoice_lines):
                self.env['sale.order.line'].create(invoice_lines)
        return invoice_lines
