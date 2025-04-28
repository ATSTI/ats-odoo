# © 2024 Carlos R. Silveira, Maurício Rodrigues Silveira, ATSti Solucoes
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Duplicar uma fatura, copiando somente produtos',
    'version': '14.0.0.1.0',
    'category': 'Localisation',
    'sequence': 2,
    'summary': 'ATSti Soluções',
    'description': """
        Cria nova account.move somente com produtos, sem serviços
        No diario diversos(general), somente para poder gerar a NFe,
        pois, na fatura consta serviços tbém, que será gerado uma nota de serviço.

        # CRON, usado para chamar a funcao copiar_fatura:
        hoje = datetime.datetime.today()
        date_min = "-".join((str(hoje.year), str(hoje.month), "01"))
        date_min = datetime.datetime.strptime(date_min, "%Y-%m-%d")
        date_max = (hoje + dateutil.relativedelta.relativedelta(months=1)).replace(day=1) - datetime.timedelta(days=1)
        msg = ''
        notas = model.search([
        ('create_date', '>=', date_min),
        ('create_date', '<=', date_max),
        ('state', '=', 'posted'),
        ('ref', 'not in', ['NFe', 'Serviço']),
        ('journal_id', '=', 1)
        ])
        #log(str(notas), level='info')
        for nf in notas:
        if nf.payment_mode_id:
            msg = 'NFe a fazer : %s' %(nf.name)
            nf.copiar_fatura()
            msg += ' , Fatura criada com sucesso'
        if msg:
            log(msg, level='info')        
    """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ["l10n_br_fiscal", "l10n_br_account_nfe"],
    'data': [
        'views/account_move_view.xml',
        # 'wizard/account_move_other_nfe_view.xml',
    ],
    'installable': True,
    'application': False,
}

