#© 2023 Carlos R. Silveira, Mauricio Silveira, ATSti Solucoes
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Envia Email',
    'version': '1.0',
    'category': 'Others',
    'sequence': 2,
    'summary': 'Enviar email vencimento do certificados',
    'description': """
        Preencher em Ações agendadas a ação:
        Envia email vencimento certificado

        "model.send_email_certificado(2, 7, 30)"
        
            2 = id do user que vai receber email, 
            7 = Dias antes de vencer, 
            30 = Outro dia antes de vencer.
    """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ['l10n_br_nfe'],
    'data': [
        'data/certificado_email_template.xml'
    ],
    'installable': True,
    'application': False,
}
