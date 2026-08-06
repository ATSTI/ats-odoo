{
    'name': 'Controle de Acesso — Condomínio',
    'version': '18.0.1.0.0',
    'summary': 'Gestão de residências, moradores e portaria',
    'category': 'Services',
    'author': 'Seu Nome',
    'depends': ['contacts', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/condo_residence_views.xml',
        'views/menuitem.xml',
        'views/condo_visitor_view.xml',
        'views/res_partner.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}