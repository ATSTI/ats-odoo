# -*- coding: utf-8 -*-
# © 2004-2010 OpenERP SA
# © 2016 Carlos Silveira <crsilveira@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Email de Aniversario',
    'version': '10.0.1.1.0',
    'category': 'Base',
    'license': 'AGPL-3',
    'author': "Carlos,"
              "ATS,"
              "",
    'website': '',
    'depends': ['partner_soma'],
    'data': [
        'views/email_niver_template.xml',
        'views/email_lista_aniversariantes.xml',
    ],
    'installable': True,
}
