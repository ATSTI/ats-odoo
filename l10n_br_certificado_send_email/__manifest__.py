# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Envia Email',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
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
    'author': 'ATSTi',
    'website': '',
    'depends': ['l10n_br_nfe'],
    'data': [
        'data/certificado_email_template.xml'
    ],
    'installable': True,
    'application': False,
}
