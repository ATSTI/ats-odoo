# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import time, datetime
import base64
# from sshtunnel import SSHTunnelForwarder
import odoorpc

from odoo.addons.br_boleto.boleto.document import Boleto

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        if 'origin' in invoice_vals:
            ctr_id = self.env['account.analytic.account'].search([('name', '=',invoice_vals['origin'])], limit=1)
            if ctr_id:
                invoice_vals['contract_id'] = ctr_id.id
                invoice_vals['journal_id'] = ctr_id.journal_id.id
        return invoice_vals


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'


    email_fat = {}

    faturar = fields.Boolean(string="Faturar")

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
        # mail = self.env['mail.thread']
        # mail.message_post(type="notification", subtype="mt_comment", **mail_details)

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
                    # 04/05/2023 Carlos, qdo dava erro nao mudava o faturar
                    contrato.write({
                        'faturar': False, 
                    })
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

        # comentar a linha abaixo  CARLOS
        # usado somente pra refazer os boletos
        #move = self.env['account.move.line'].search([('move_id', '=' ,move)],limit=1)


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

            # coloquei isso pois preciso excluir o boleto errado
            tem_boleto = attachment_obj.search([
                ('name', '=', name), 
                ('res_model', '=', 'account.invoice'), 
                ('res_id','=',item.id)
            ])
            if tem_boleto:
                tem_boleto.unlink()


            boleto_id = attachment_obj.create(dict(
                    name=name,
                    datas_fname=name,
                    datas=base64.b64encode(boleto),
                    mimetype='application/pdf',
                    res_model='account.invoice',
                    res_id=item.id,
                ))
        return boleto

    """ 5X - Gerando o boleto quando este ja foi criado e estava com erro """
    def criar_boleto_novamente(self, id_invoice=None):
        boleto = False
        if not id_invoice:
            invoice_ids = self.env['account.invoice'].search([
                ('date_due', '=', '2024-12-10'),
                ('payment_mode_id', '=', 3),
                ('state', '=', 'open'),
                ('create_date', '>', '2024-12-01 19:00:00'),
                ('comment', '=', ''),
            ],)
        else:
            #invoice_ids = self.env['account.invoice'].browse([invoice])
            invoice_ids = self.env['account.invoice'].browse([id_invoice])
        
        # comentar a linha abaixo  CARLOS
        # usado somente pra refazer os boletos
        #move = self.env['account.move.line'].search([('move_id', '=' ,move)],limit=1)
        for invoice_id in invoice_ids[:50]:
            if 'Bol' in invoice_id.comment:
                continue
            move = invoice_id.receivable_move_line_ids
            invoice_id.comment += 'Bol'
            #self.env['payment.order.line'].action_register_boleto(
            #    invoice_ids.receivable_move_line_ids)
            name = "boleto-%s-%s.pdf" % (
                   invoice_id.number, invoice_id.partner_id.commercial_partner_id.name)
            attachment_obj = self.env['ir.attachment']

            # coloquei isso pois preciso excluir o boleto errado
            tem_boleto = attachment_obj.search([
                    ('name', '=', name), 
                    ('res_model', '=', 'account.invoice'), 
                    ('res_id','=',invoice_id.id)
            ])
            if tem_boleto:
                if tem_boleto.create_date > datetime.datetime.strptime('2024-12-03 9:00:00', '%Y-%m-%d %H:%M:%S'):
                    continue
 
            print(f"Fatura : {invoice_id.number} - cliente: {invoice_id.partner_id.name}")
            boleto_nome = '%s%s%s-%s.pdf' %(
                    str(move.date.day).zfill(2),
                    str(move.date.month).zfill(2),
                    str(move.date.year),
                    move.move_id.name
                )
        
            boleto_report = self.env['ir.actions.report'].search(
                [('report_name', '=',
                'br_boleto.report.print')])
            report_service = boleto_report.xml_id
            boleto, dummy = self.env.ref(report_service).render_qweb_pdf(
                [invoice_id.id])

            if boleto:
                if tem_boleto:
                    tem_boleto.unlink()


                boleto_id = attachment_obj.create(dict(
                    name=name,
                    datas_fname=name,
                    datas=base64.b64encode(boleto),
                    mimetype='application/pdf',
                    res_model='account.invoice',
                    res_id=invoice_id.id,
                ))
        return boleto

    """ 3 - Executa o faturamento das vendas existentes """
    def faturar_invoice(self, partner):
        mes = fields.date.today().month
        ano = fields.date.today().year
        if fields.date.today().day < 10:
            mes = mes - 1
            if mes == 0:
                mes = 12
                ano = ano - 1
        mes_ant = '%s-%s-05 01:00:00' %(ano, mes)
        venda = self.env['sale.order']
        venda_ids = venda.search([
            ('partner_id','=', partner),
            ('state', '=', 'sale'),
            ('confirmation_date','>', mes_ant),
            ('invoice_status', '=', 'to invoice')
        ])
        if venda_ids:
            id = venda_ids.action_invoice_create()
            return id
        else:
            return False

    @api.multi
    def _create_invoice(self):
        invoice_ids = []
        invoice_vals = self._prepare_invoice()
        msg_erro = ''
        invoice_ja_gerada = 'N'
        if msg_erro == '':
            #mes = fields.date.today().month
            #ano = fields.date.today().year
            #if fields.date.today().day > 10:
            #    # mes seguinte
            #    mes += 1
            #    if mes == 13:
            #        mes = 1
            #        ano += 1
            reference = invoice_vals['reference']
            #data_vencimento_fatura = '2024-10-10' # invoice_vals['date_due']
            #        ('date_due', '=', data_vencimento_fatura),
            #'%s-%s-%s' %(self.name, str(mes).zfill(2), ano)
            invoice = self.env['account.invoice'].search([
                    ('partner_id','=', self.partner_id.id),
                    ('reference', '=', reference),
            ], limit=1)
            if invoice:
                msg_erro = ''
                #print ('invoice encontrada @@@@@@ : %s, %s' %(reference, invoice.id))
                invoice = False
                return invoice, msg_erro

            invoice_vals['partner_shipping_id'] = invoice_vals['partner_id']
            inv_lines = self._prepare_order_lines(self)
            if inv_lines:
                msg_erro = 'Erro para criar Pedido Venda.'
                invoice_vals['order_line'] = inv_lines
                # 2022 testando se já gerou a venda pra nao gerar novamente
                venda = self.env['sale.order']
                venda_ids = venda.search([
                    ('partner_id','=', self.partner_id.id),
                    ('reference', '=', reference),
                ])
                if venda_ids:
                    invoice_ja_gerada = 'S'
                    invoice_ids = venda_ids
                else:
                    invoice_ids.append(self.env['sale.order'].create(invoice_vals))
            else:
                msg_erro = 'Sem itens para Faturar.'
                return False, msg_erro
            msg_erro = 'Erro pra confirmar pedido de venda.'
            #invoice_ids[0].onchange_partner_id()
            #invoice_ids[0].write({
            #    'payment_term_id': invoice_vals['payment_term_id'], 
            #    'partner_invoice_id': self.partner_id.id
            #    })
            if invoice_ids[0].state == 'draft':
                invoice_ids[0].action_confirm()
            invoice = self.env['account.invoice'].search([
                    ('partner_id','=', self.partner_id.id),
                    ('reference', '=', reference),
            ])
            if invoice:
                msg_erro = ''
                invoice_ja_gerada = 'S'
            else:
                msg_erro = 'Erro para criar a Fatura.'
                inv_id = self.faturar_invoice(invoice_vals['partner_id'])
                if not inv_id:
                    print ('Erro contrato %s' %(self.partner_id.name))
                    return False, msg_erro
                invoice = self.env['account.invoice'].browse(inv_id)
                if invoice.partner_id.street2 and 'MAKIN' in invoice.partner_id.street2.upper():
                    invoice.write({'contract_id': self.id, 'local': 'MAKIN'})
                else:
                    if invoice.partner_id.district:
                        invoice.write({
                            'contract_id': self.id, 
                            'local': invoice.partner_id.district
                        })
                    else:
                        invoice.write({'contract_id': self.id})
                if invoice.journal_id != self.journal_id:
                    if self.journal_id:
                        invoice.write({'journal_id': self.journal_id.id})
                if not invoice.payment_mode_id:
                    if self.payment_mode_id:
                        invoice.write({'payment_mode_id': self.payment_mode_id.id})
                msg_erro = 'Erro para Confirmar a Fatura.'
                invoice.action_invoice_open()
                if invoice.payment_mode_id.boleto_type:
                    msg_erro = 'Erro para Gerar o Boleto.'
                    #if invoice.partner_id.id == 1079:
                    #print('XXXXX %s' %(invoice.partner_id.name))
                    try:
                        self.criar_boleto(invoice.id, invoice.receivable_move_line_ids[0])
                    except:
                        print ('Erro para criar boleto : %s, contrato : %s' %(invoice.partner_id.name, reference))
                msg_erro = ''
                if invoice_ja_gerada == 'S':
                    msg_erro = 'S'
            return invoice, msg_erro

    @api.multi
    def recurring_create_invoice(self, contratos, cron=False):
        if not cron:
            contratos = self.id
        context = {}
        email_line = {}
        email_rel = {}
        ctr = self.browse(contratos)
        for contract in ctr:
            # if not contract.active:
            #     continue
            # if not contract.partner_id.active:
            #     continue
            # context['cliente'] = contract.partner_id
            # context['contrato'] = contract
            # #context['empresa'] = contract.company_id
            # context['id_contrato'] = contract.id
            # valido = self.validando_info(context)
            # if len(valido):
            #     # 01/02/2022 estava no write abaixo : nada haver , 'state': 'draft'
            #     contract.write({'msg_faturamento': valido})
            #     email_line = {'faturado':'NAO',
            #         'contrato': contract.code,
            #         'cliente': contract.partner_id.name,
            #         'ocorrencia': valido
            #     }
            #     email_dados = email_rel.setdefault(id,email_line)
            #     email_dados.setdefault('NAO FATURADO', {})
            #     contract.message_post(body=_(email_dados))
            #     continue
            old_date = fields.Date.from_string(
                contract.recurring_next_date or fields.Date.today())
            new_date = old_date + self.get_relative_delta(
                contract.recurring_rule_type, contract.recurring_interval)
            ctx = self.env.context.copy()
            ctx.update({
                'old_date': old_date,
                'next_date': new_date,
                'faturar': False, 
                # Force company for correct evaluate domain access rules
                #'force_company': contract.company_id.id,
            })
            # Re-read contract with correct company
            contract.msg_faturamento = 'Faturado'

            inv, msg = contract.with_context(ctx)._create_invoice()
            #if not inv:
            #    fat_erro = 'FATURA NÃO CRIADA : %s - %s' %(contract.name, contract.id)
            #    print(fat_erro)
            #else:
            #    print('xxxxxxxxxx ctr: %s - %s' %(inv.name, inv.id))
            if inv and msg == '':
                #print('xxxxxxxxxx ctr: %s - %s' %(inv.name, inv.id))
                contract.write({
                    'recurring_next_date': new_date.strftime('%Y-%m-%d'),
                    'faturar': False, 
                })
                #self.env.cr.commit()
            else:
                if msg != 'S':
                    msg = 'Erro no faturamento,  ' + msg
                    contract.message_post(body=_(msg))
                    # 01/02/2022 tirei , 'state': 'draft'
                    # 04/05/2023 Carlos, qdo dava erro nao mudava o faturar
                    contract.write({'msg_faturamento': msg, 'faturar': False})
                    #self.relatorio_faturamento('NAO', contract.id, contract.code, contract.partner_id.name,
                    #   'Erro ao executar o faturamento.', 'NAO', contract.company_id.name)

                # odoo runbot
                odoobot_id = self.env['ir.model.data'].sudo().xmlid_to_res_id("base.partner_root")

                ch_obj = self.env['mail.channel']
                channel = ch_obj.sudo().search([('name', 'ilike', 'geral')])
                if channel:
                    # send a message to the related user
                    fat_erro = 'Contrato não faturado : %s - %s - %s' %(contract.id, contract.name, contract.partner_id.name)
                    channel.sudo().message_post(
                            body=fat_erro,
                            author_id=odoobot_id,
                            message_type="comment",
                            subtype="mail.mt_comment",
                    )

        #if len(email_rel):
        #    ir_model_data = self.env['ir.model.data']
        #    try:
        #        template_id = ir_model_data.get_object_reference('contract_billing', 'email_erro_fatura')[1]
        #    except ValueError:
        #        template_id = False
        #    context['data'] = email_rel
        #    #self.env['mail.template'].browse(template_id).send_mail(contract.id, force_send=True)
        self.relatorio_faturamento()
        return True

    @api.model
    def cron_recurring_create_invoice(self):
        #     ('state', '=', 'done'),
        contracts = self.search(
            [('recurring_next_date', '<=', fields.date.today()),
             ('recurring_next_date', '>', '2024-09-01'),
             ('recurring_invoices', '=', True),
             ('active','=', True),
             ('faturar', '=', True),
            ], limit=10)
        #contracts = self.browse([100])
        total = 0
        context = {}
        email_line = {}
        email_rel = {}
        contratos = []
        for contract in contracts:
            if not contract.active:
                continue
            if not contract.partner_id.active:
                # odoo runbot
                odoobot_id = self.env['ir.model.data'].sudo().xmlid_to_res_id("base.partner_root")

                ch_obj = self.env['mail.channel']
                channel = ch_obj.sudo().search([('name', 'ilike', 'geral')])
                if channel:
                    # send a message to the related user
                    fat_erro = 'Associado com cadastro inativo : %s - %s - %s' %(contract.id, contract.name, contract.partner_id.name)
                    channel.sudo().message_post(
                            body=fat_erro,
                            author_id=odoobot_id,
                            message_type="comment",
                            subtype="mail.mt_comment",
                    )
                continue
            context['cliente'] = contract.partner_id
            context['contrato'] = contract
            #context['empresa'] = contract.company_id
            context['id_contrato'] = contract.id
            valido = self.validando_info(context)
            if len(valido):
                # 01/02/2022 estava no write abaixo : nada haver , 'state': 'draft'
                contract.write({'msg_faturamento': valido})
                email_line = {'faturado':'NAO',
                    'contrato': contract.code,
                    'cliente': contract.partner_id.name,
                    'ocorrencia': valido
                }
                email_dados = email_rel.setdefault(id,email_line)
                email_dados.setdefault('NAO FATURADO', {})
                contract.message_post(body=_(email_dados))
                continue
            contratos.append(contract.id)
            total += 1
            if total == 20:
                break

        return self.recurring_create_invoice(contratos, True)

    def _prepare_order_lines(self, contract):
        inv_lines = []
        for line in contract.recurring_invoice_line_ids:
            invoice_lines = {}
            # TODO USAR as DATAS
            fatura = True
            if line.date_start and line.date_start > self.recurring_next_date:
                fatura = False
            if line.date_stop and line.date_stop < self.recurring_next_date:
                fatura = False
            if fatura:
                invoice_lines = {
                        'name': line.name,
                        'price_unit': line.price_unit or 0.0,
                        'product_uom_qty': line.quantity,
                        'product_id': line.product_id.id or False,
                }
                inv_lines.append((0, 0, invoice_lines))
        return inv_lines
