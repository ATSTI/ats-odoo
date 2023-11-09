    # Copyright 2021 Atsti - Mauricio Silveira
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from datetime import datetime, date, timedelta
from dateutil.relativedelta import *


class AccountAnalyticAccount(models.Model):
    _inherit = 'contract.contract'
    
    tipo = fields.Selection(
        selection=[
            ('seguro', 'Seguro'),
            ('previdencia', 'Previdência'),
            ('consorcio', 'Consórcio'),
            ('saude', 'Saúde'),
            ('cartadefianca', 'Carta de Fiança'),
            ('fiancalocativa', 'Fiança Locativa'),
            ('emprasar', 'Emprasarial'),
            ('capitali', 'Capitalização'),
            ('rc', 'RC'),
         ],
    )
    tipo_seguro = fields.Selection(
        selection=[
            ('vida', 'Seg. de Vida'),
            ('carro', 'Seg. de Carro'),
            ('casa', 'Seg. de Casa'),
            ('animais', 'Seg. de Animais'),
            ('outros', 'Outro Seg.'),
            ('cavalo', 'Cavalo'),
            ('residen', 'Residencial'),
            ('auto', 'Auto'),       
            ('dit', 'DIT'),       
        ]
    )
    forma_de_pag = fields.Selection(string="Forma de pagamento",
        selection=[
            ('deb', 'Debito'),
            ('cred', 'Credito'),
            ('bole', 'Boleto'),
         ],
    )
    # propos = fields.Selection(
    #     selection=[
    #         ('cota', 'Cotação'),
    #         ('proposta', 'Proposta'),
    #         ('apolice', 'Apolice'),
    #      ],required=True,
    # )
    valorl = fields.Float('Valor Liquido')
    cmssao = fields.Float('Comissao')
    descr = fields.Char('Descricao')
    cod_seguro = fields.Char('Placa/Nome')
    corretora_id = fields.Many2one(
        comodel_name="res.partner",
        string="Seguradora/Administradora",
    )
    #previdencia = fields.Char('Previdencia')
    vencimentos = fields.Char(
        compute="_compute_vencimentos",
        string="Dia vencimentos",
        store=True,
    )

    @api.model
    def cron_send_vcto(self,tempo_vencimento):
        # su_id = self.env['account.move.line'].browse(SUPERUSER_ID)
        domain=[('name','like','Email apolices')]
        template_browse = self.env['mail.template'].search(domain, limit=1)
        data_hoje = date.today()
        data_fim = data_hoje + timedelta(days=tempo_vencimento+1)
        data_hoje = data_hoje - timedelta(days=1)
        contract_ids = self.env['contract.contract'].search([
                ('state', '=', 'done'),
                ('date_end', '>', data_hoje),
                ('date_end', '<', data_fim),
        ])
        tabela = '<table border="1" width="100%">\
                      <tr>\
                      <th>Cliente</th>\
                      <th>Tipo</th>\
                      <th>Data Vencimento</th>\
                      <th>Email</th></tr>'
        # emails vencimento parcela
        linha = ''
        for inv in contract_ids:
            prt = inv.contract_id.partner_id
            # if not prt.email:

            email = prt.email
            vcto = inv.date_end
            vcto = '%s-%s-%s' %(str(vcto.day).zfill(2), str(vcto.month).zfill(2), 
                    str(vcto.year))
            nome = prt.name.split(None, 1)
            linha += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' %(
                nome, inv.tipo_seguro, vcto, email 
            )
            tabela += linha
            if template_browse:
                # template_browse['email_to'] = 'carlos@atsti.com.br'
                template_browse['body_html'] = tabela
                template_browse.send_mail(inv.id, force_send=True)

    @api.model
    def enviar_email_lembrete(self):
        template_id = self.env['ir.model.data'].get_object_reference('contract_corretora',
                                                                     'email_lembrete_parcela')[1]
        template_browse = self.env['mail.template'].browse(template_id)
        data_hoje = date.today()
        data_fim = data_hoje + timedelta(days=1)
        if data_hoje.weekday() == 5:
            # sabado, ja foi
            return True
        if data_hoje.weekday() == 6:
            # domingo, ja foi
            return True
        if data_hoje.weekday() == 4:
            data_hoje = data_hoje - timedelta(days=1)
            data_fim = data_hoje + timedelta(days=4)
            invoice_ids = self.env['contract.line'].search([
                ('dia_vencimento', '>', data_hoje.day),
                ('dia_vencimento', '<', data_fim.day),
            ])
        else:
            #data_hoje.day
            invoice_ids = self.env['contract.line'].search([
                ('dia_vencimento', '=', data_hoje.day),
            ])
        # emails vencimento parcela
        email_gerencia = '<strong>Relatório dos envios de lembrete</strong>'
        email_gerencia += '<table border="1" width="100%">'
        email_gerencia += '<tr><th>Cliente</th><th>Contrato</th><th>Enviado</th><th>Motivo</th></tr>'
        for inv in invoice_ids:
            ctr_email = inv.contract_id
            email_gerencia += '<tr><td>%s</td><td>%s</td>' %(ctr_email.partner_id.name, ctr_email.name)
            #if inv.contract_id.id == 601:
            #    import pudb;pu.db
            if not inv.date_end:
                email_gerencia += '<td><strong>Não</strong></td><td>Sem fim da vigência</td></tr>'
                continue

            # se 1 parcela e pagou no mesmo mes entao nao tem mais
            if inv.dia_vencimento > inv.date_start.day and inv.quantity == 1:
                email_gerencia += '<td><strong>Não</strong></td><td>1 parcela, já enviado</td></tr>'
                continue

            #mes_hoje_end = inv.date_end + relativedelta(day=31)
            # Pega o primeiro dia do proximo mes
            mes_hoje_end = (inv.date_end.replace(day=1) + timedelta(days=32)).replace(day=1)
            if mes_hoje_end < data_fim:
                #print("nao enviado %s" %(inv.contract_id.partner_id.name))
                vg = inv.date_end
                vg = '%s-%s-%s' %(str(vg.day).zfill(2), str(vg.month).zfill(2), 
                str(vg.year))
                email_gerencia += '<td><strong>Não</strong></td><td>Encerrado %s</td></tr>' %(vg)
                continue

            # o campo quantidade e usado para o numero de parcelas
            mes_hoje = inv.date_start + relativedelta(months=+int(inv.quantity))
            mes_hoje = mes_hoje + relativedelta(day=31)
            if data_hoje > mes_hoje:
                email_gerencia += '<td><strong>Não</strong></td><td>O numero informado em quantidade já enviado.</td></tr>'
                continue

            prt = inv.contract_id.partner_id
            if not prt.email:
                email_gerencia += '<td><strong>Não</strong></td><td>Sem email.</td></tr>'
                continue

            tipo = 'normal'
            seguro = ''
            
            seguro = inv.name
            if inv.product_id.name == 'Animal':
                tipo = 'animal'
            email_to = prt.email
            corpo = '<br />'           
            if prt.parent_id:
                corpo += '<p>%s Bom dia,</p>' %(prt.parent_id.name)
            else:
                corpo += '<p>%s Bom dia,</p>' %(prt.name)
            corpo += '<p>Tudo bem por ai ?? </p>'
            corpo += '<br />'
            corpo += '<br />'
            valor = "{:.2f}".format(inv.price_unit)
            vcto = inv.dia_vencimento
            vcto = '%s-%s-%s' %(str(vcto).zfill(2), str(data_hoje.month).zfill(2), 
                str(data_hoje.year))
            if inv.price_unit > 999:
                valor = str(valor).replace('.',',')
            else:
                valor = str(valor).replace('.',',')
            if tipo == 'animal':
                corpo += '<p>Informamos que o vencimento da parcela do seu seguro Cavalo está programada para:'
            else:
                corpo += 'Informamos abaixo o vencimento da parcela do seu seguro :'
                corpo += '<br />'
                corpo += '%s, ' %(seguro)
            corpo += '<br />'
            corpo += 'Vencimento %s.' %(vcto)
            corpo += '<br />'
            #if inv.price_unit:
            #    corpo += 'Valor de R$ %s.' %(valor)
            corpo += '<br />'
            corpo += '<br />'
            corpo += '<p>Qualquer duvida favor entrar em contato pelo telefone :</p>'
            corpo += '<br />'
            corpo += '<p>Marcia (11) 99946-0450</p>'
            corpo += '<p>Marcio (19) 99198-8839</p>'
            corpo += '<br />'
            corpo += '<p>Atenciosamente,</p>'
            corpo += '<br />'
            corpo += '<br />'
            corpo += '<p>Soma Corretora de Seguros</p>'
            corpo += ''
            corpo += ''
            if template_browse:
                values = template_browse.generate_email(prt.id, fields=None)
                #template_browse.email_to = email_to
                #template_browse['body_html'] = corpo
                #template_browse.send_mail(inv.analytic_account_id.id, force_send=True)
                #template_browse.email_to = 'marcio@somaseguros.com.br'
                values['email_to'] = email_to
                values['email_from'] = 'financeiro@somaseguros.com.br'
                if inv.contract_id.user_id and 'marcia@soma' not in inv.contract_id.user_id.email:
                    values['email_cc'] = 'marcia@somaseguros.com.br,' + inv.contract_id.user_id.email
                values['res_id'] = False
                values['body_html'] = corpo
                values['model'] = 'contract.contract'
                values['res_id'] = inv.contract_id.id 
                if not values['email_to'] and not values['email_from']:
                    pass
                mail_mail_obj = self.env['mail.mail']
                msg_id = mail_mail_obj.sudo().create(values)
                if msg_id:
                    mail_mail_obj.send(msg_id)
                    email_gerencia += '<td>Enviado</td><td></td></tr>'

        email_gerencia += '</table>'

        # emails para o administrador
        # emails vencimento parcela
        #domain=[('name','like','Email Parcelas Administrador')]
        #template_browse = self.env['mail.template'].search(domain, limit=1)

        tabela = '<table border="1" width="100%">\
                        <tr>\
                        <th>Cliente</th>\
                        <th>Tipo</th>\
                        <th>Data Vencimento</th>\
                        <th>Valor</th></tr>'
        lista = ''
        for inv in invoice_ids:
            prt = inv.contract_id.partner_id
            vcto = inv.dia_vencimento
            vcto = '%s-%s-%s' %(str(vcto).zfill(2), str(data_hoje.month).zfill(2), 
            str(data_hoje.year))
            valor = "{:.2f}".format(inv.price_subtotal)
            valor = str(valor).replace('.',',')
            situacao = '** Sem Email **'
            prt_id = inv.contract_id.partner_id
            if prt_id.email:
                situacao = 'Enviado'
            if inv.contract_id.tipo_seguro: 
                tipo = '%s-%s' %(inv.contract_id.tipo,inv.contract_id.tipo_seguro)
            else:
                tipo = '%s' %(inv.contract_id.tipo)
            # for inv in inv.invoice_id.invoice_line_ids:
            #     seguro = inv.name
            lista += '<tr><td>%s</td><td>%s</td><td>%s</td><td align="right">%s</td></tr>' %(
            prt_id.name, tipo, vcto, valor)

        if lista != '':
            lista = tabela + lista + '</table>'
            lista = 'Lista de Vencimento de Parcelas:<br />' + lista + '<br />' + email_gerencia 
            #if template_browse:
            #    template_browse['body_html'] = lista
            #    template_browse['email_to'] = 'financeiro@somaseguros.com.br'
            #    template_browse.send_mail(inv.contract_id.id, force_send=True)
            try:
                vals = {
                    'subject': 'Lista de vencimento de Parcelas',
                    'body_html': lista,
                    'email_to': 'financeiro@somaseguros.com.br',
                    'email_from': 'marcio@somaseguros.com.br',
                    'auto_delete': False,
                    'mail_server_id': 4,
                }
                mail_id = self.env['mail.mail'].sudo().create(vals)
                mail_id.sudo().send()
            except:
                lista = ''

    @api.multi
    @api.depends('contract_line_ids')
    def _compute_vencimentos(self):
        for rec in self:
            for linha in rec.contract_line_ids:
                if linha.dia_vencimento:
                    if rec.vencimentos:
                        rec.vencimentos += ', ' + str(linha.dia_vencimento)
                    else:
                        rec.vencimentos = str(linha.dia_vencimento)


class AccountAnalyticContractLine(models.Model):
    _inherit = 'contract.line'

    dia_vencimento = fields.Integer('Dia vencimento')
    data_fim_vencimento = fields.Date('Data último vencimento')

    # coloquei um compute acima
    #def write(self, vals):
    #    res = super(AccountAnalyticContractLine, self).write(vals)
    #    if 'dia_vencimento' in vals:
    #        if self.contract_id.vencimentos:
    #            self.contract_id.vencimentos = self.contract_id.vencimentos + ', ' + vals['dia_venciemnto']
    #        else:
    #            self.contract_id.vencimentos = vals['dia_venciemnto']
    #    return res
