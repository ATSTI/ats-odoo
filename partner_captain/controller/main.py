from odoo import http
from odoo.http import request


class CaptainSizeTable(http.Controller):

    @http.route('/captain/size/table', type='http', auth='user', website=False)
    def size_table(self, genero=None, selecao=None, **kw):

        domain = []
        if genero:
            domain.append(('genero', '=', genero))
        if selecao:
            domain.append(('selecao', '=', selecao))

        records = request.env['captain.size.rule'].search(domain)

        alturas = sorted(set(records.mapped('altura')))
        pesos = sorted(set(records.mapped('peso')))

        # matriz = {altura: {peso: tamanho}}
        matrix = {}
        for r in records:
            matrix.setdefault(r.altura, {})
            matrix[r.altura][r.peso] = r.tamanho

        return request.render(
            'partner_captain.report_captain_size_rule_html',
            {
                'alturas': alturas,
                'pesos': pesos,
                'matrix': matrix,
                'genero': genero,
                'selecao': selecao,
            }
        )
