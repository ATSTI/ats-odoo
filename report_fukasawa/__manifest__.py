# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Relatórios personalizados Fukasawa',
    'author': 'Odoo S.A',
    'category': 'Others',
    'description': """Customização para o Fukasawa, POS e ACCOUNT relatorios""",
    'license': 'LGPL-3',
    'depends': ['point_of_sale', 'account'],
    'data': [
        'report/report_paper_format_fukasawa.xml',
        'report/report_delivery_document_fukasawa.xml',
    ],
    'qweb': [
        'static/src/xml/OrderReceipt.xml',
    ],
    'auto_install': False,
}
