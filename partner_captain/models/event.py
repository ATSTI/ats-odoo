from odoo import models, fields
import xlsxwriter
import io
import base64
class EventEvent(models.Model):
    _inherit = 'event.event'

    staff_ids = fields.Many2many(
        'res.users',
        'event_staff_rel',
        'event_id',
        'user_id',
        string="Staff Responsáveis"
    )
    def action_call_equipamentos(self):
        for event in self:
            registrations = self.env['event.registration'].search([
                ('event_id', '=', event.id)
            ])
            registrations._assign_equipamentos()
        return True
    
    def action_limpar_equipamentos(self):
        for event in self:
            event.registration_ids.action_limpar_equipamento()
        return True

    def color_by_situacao(self, product):
        if not product:
            return '#ffffff'

        return {
            'otima': '#c8f7c5',
            'bom': '#e3f9c6',
            'medio': '#fff3b0',
            'ruim': '#ffd6a5',
            'pessimo': '#ffadad',
        }.get(product.situacao, '#ffffff')
    
    def action_export_equipamentos_excel(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('EQUIPAMENTOS')

        header_format = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })

        cell_format = workbook.add_format({
            'border': 1,
            'align': 'center',
        })

        text_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'text_wrap': True,
        })

        headers = [
            'PARTICIPANTE', 'GENERO', 'PESO', 'ALTURA',
            'EVENTO', 'NADADEIRA',

            'BCD', 'TAG BCD',

            'SUIT', 'TIPO SUIT', 'TAG SUIT',

            'REGULADOR', 'TIPO REG', 'TAG REG',

            'BAG', 'TAG BAG',

            'OBSERVAÇÃO'
        ]

        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
            worksheet.set_column(col, col, 20)
        worksheet.set_column(len(headers) - 1, len(headers) - 1, 35)

        row = 1

        for event in self:
            for reg in event.registration_ids:
                worksheet.write(row, 0, (reg.partner_id.name or '').upper(), cell_format)
                worksheet.write(row, 1, (reg.genero or '-').upper(), cell_format)
                worksheet.write(row, 2, reg.peso or '-', cell_format)
                worksheet.write(row, 3, reg.altura or '-', cell_format)
                worksheet.write(row, 4, (reg.tipo_evento or '-').upper(), cell_format)
                worksheet.write(row, 5, (reg.nadadeira or '-').upper(), cell_format)
                if reg.bcd_info:
                    worksheet.write(row, 6, 'EQUIPAMENTO PRÓPRIO', cell_format)
                    worksheet.write(row, 7, '-', cell_format)
                elif reg.bcd_id:
                    worksheet.write(row, 6, reg.bcd_id.display_name.upper(), cell_format)
                    worksheet.write(row, 7, (reg.bcd_id.product_tmpl_id.tag_cd or '-').upper(), cell_format)
                else:
                    worksheet.write(row, 6, '-', cell_format)
                    worksheet.write(row, 7, '-', cell_format)
                if reg.suit_info:
                    worksheet.write(row, 8, 'EQUIPAMENTO PRÓPRIO', cell_format)
                    worksheet.write(row, 9, '-', cell_format)
                    worksheet.write(row, 10, '-', cell_format)
                elif reg.suit_id:
                    worksheet.write(row, 8, reg.suit_id.display_name.upper(), cell_format)
                    worksheet.write(row, 9, (reg.suit_id.product_tmpl_id.tipo_suit or '-').upper(), cell_format)
                    worksheet.write(row, 10, (reg.suit_id.product_tmpl_id.tag_cd or '-').upper(), cell_format)
                else:
                    worksheet.write(row, 8, '-', cell_format)
                    worksheet.write(row, 9, '-', cell_format)
                    worksheet.write(row, 10, '-', cell_format)
                if reg.reg_info:
                    worksheet.write(row, 11, 'EQUIPAMENTO PRÓPRIO', cell_format)
                    worksheet.write(row, 12, '-', cell_format)
                    worksheet.write(row, 13, '-', cell_format)
                elif reg.reg_id:
                    worksheet.write(row, 11, reg.reg_id.display_name.upper(), cell_format)
                    worksheet.write(row, 12, (reg.reg_id.product_tmpl_id.tipo_reg or '-').upper(), cell_format)
                    worksheet.write(row, 13, (reg.reg_id.product_tmpl_id.tag_cd or '-').upper(), cell_format)
                else:
                    worksheet.write(row, 11, '-', cell_format)
                    worksheet.write(row, 12, '-', cell_format)
                    worksheet.write(row, 13, '-', cell_format)
                if reg.bag_info:
                    worksheet.write(row, 14, 'EQUIPAMENTO PRÓPRIO', cell_format)
                    worksheet.write(row, 15, '-', cell_format)
                elif reg.bag_id:
                    worksheet.write(row, 14, reg.bag_id.display_name.upper(), cell_format)
                    worksheet.write(row, 15, (reg.bag_id.product_tmpl_id.tag_cd or '-').upper(), cell_format)
                else:
                    worksheet.write(row, 14, '-', cell_format)
                    worksheet.write(row, 15, '-', cell_format)
                worksheet.write(row, 16, reg.obs or '-', text_format)
                row += 1

        workbook.close()
        output.seek(0)

        attachment = self.env['ir.attachment'].create({
            'name': f'EQUIPAMENTOS_{self.name}.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'res_model': 'event.event',
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

