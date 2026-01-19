from odoo import api, fields, models, _, tools


class ListaEquipamentos(models.Model):
    _name = "lista.equipamentos"
    _auto = False

    partner_id = fields.Many2one('res.partner', string='Parceiro')
    equipamento = fields.Char(string='Equipamento')
   
    _order = "partner_id"
    

    def init(self):
        tools.drop_view_if_exists(self._cr, 'lista_equipamentos')
        self._cr.execute("""
            CREATE OR REPLACE VIEW lista_equipamentos AS (
                SELECT distinct ph.partner_id as id,  ph.partner_id, 
                  array_to_string(array(select chn.name from partner_historico phi
                  inner join crm_historico_partner_historico_rel cx on phi.id = cx.partner_historico_id 
                  inner join crm_historico chn on chn.id = cx.crm_historico_id
                  where phi.partner_id = ph.partner_id),',') as equipamento
                  from partner_historico ph)""")

