# Copyright 2020 ForgeFlow S.L. (https://forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "ATSti",
    "version": "14.0.1.1.0",
    "category": "maintenance",
    "description" : "Cria retorno para o estoque quando a OM e concluida. \
        IMPORTANTE: \
            - Necessario criar um tipo de operação \
              no inventário: Manutenção \
              com local origem Manutenção e destino Stock. \
            - O estágio de Concluído precisa estar marcado como 'Chamdo atendido'",
    "author": "Mauricio, ATSTi Soluções",
    "website": "",
    "license": "LGPL-3",
    "depends": ["maintenance", "maintenance_request_stage_transition"],
    "data": [
        "views/maintenance_picking_views.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
    "application": False,
}
