from odoo import api, fields, models, _, tools


class AccountMoveReportRec(models.Model):
    _name = "account.move.report.rec"
    _auto = False

    partner_id = fields.Many2one('res.partner', string='Parceiro')
    vendedor_id = fields.Many2one('res.users', string='Vendedor')
    cliente = fields.Char(string='Fornecedor')
    fatura = fields.Integer(string='Fatura/NFe')
    lancamento = fields.Char(string='Lancamento')
    forma_pagto = fields.Char(string='Forma Pagamento')
    date = fields.Date(string='Data')
    data_vcto = fields.Date(string='Data Vencimento')
    data_pagto = fields.Date(string='Data Pagamento')
    vlr_fatura = fields.Float(string='Valor Fatura')
    saldo = fields.Float(string='Saldo')
    recebido = fields.Float(string='Recebido')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    dias = fields.Integer(string='Dias')
    account_id = fields.Many2one('account.account', string='Account')
    move_id = fields.Many2one('account.move', string='Journal Entry')
    journal_id = fields.Many2one('account.journal', string='Journal')

    _order = "data_vcto, cliente"
    
    """
    @api.multi
    def vencimentos_ids(self):
        import pudb;pu.db
        vcto = []
        for vc in self:
            vcto['dta'] = vc.data_vcto
        return vcto
    """    

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'account_move_report_rec')
        self._cr.execute("""
            CREATE OR REPLACE VIEW account_move_report_rec AS (
                SELECT 
                    aml.id as id
                    , aml.partner_id 
                    ,COALESCE(rp.ref, to_char(rp.id, '99999')) || '-' || rp.name
                    || '(' || rp.cnpj_cpf || ')' as cliente
                    ,ai.nfe_number_static as fatura
                    , (SELECT iv.name FROM account_move_line iv 
                        where iv.invoice_id = aml.invoice_id 
                          and product_id is not null LIMIT 1) as LANCAMENTO
                    ,(SELECT aj.name FROM account_move_line ap,
                         account_journal aj 
                         WHERE ap.journal_id = aj.id 
                           AND ap.full_reconcile_id = aml.full_reconcile_id
                           AND ap.debit = 0
                         order by ap.id desc limit 1) as forma_pagto
                    ,aml.date     
                    ,aml.date_maturity as data_vcto
                    ,(SELECT COALESCE(ap.date, Null) FROM account_move_line ap
                         WHERE ap.full_reconcile_id = aml.full_reconcile_id
                           AND ap.debit = 0
                         order by aml.id desc limit 1) as data_pagto
                    ,aml.debit as vlr_fatura 
                    ,aml.amount_residual as saldo
                    ,(aml.debit - aml.amount_residual) as recebido
                    ,aml.company_id
                    ,(aml.date_maturity - '2000-01-01') as dias
                    ,aml.account_id 
                    ,aml.move_id
                    ,aml.journal_id
                    ,ai.user_id as vendedor_id
                FROM account_move_line aml
                    ,res_partner rp 
                    ,account_invoice ai
                    ,account_account aa
                WHERE aml.partner_id = rp.id 
                AND aml.invoice_id = ai.id 
                AND aa.id = aml.account_id 
                AND aa.user_type_id = 1
                AND aml.debit > 0
                AND ai.type = 'out_invoice'
                AND tax_line_id is null 
                ORDER BY aml.date_maturity          
            )""")
        #    AND aa.internal_type = 'receivable' 
        #self.vencimentos_ids()
