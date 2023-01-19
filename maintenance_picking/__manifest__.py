# Copyright 2020 ForgeFlow S.L. (https://forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "ATSti",
    "version": "14.0.1.1.0",
    "category": "maintenance",
    "description" : "Cria retorno para o estoque quando a OM e concluida. \
        IMPORTANTE: necessario criar um tipo de operação \
            no inventário: Manutenção \
            com local origem Manutenção e destino Stock",
    "author": "Mauricio, ATSTi Soluções",
    "website": "",
    "license": "LGPL-3",
    "depends": ["maintenance"],
    "data": [
        "views/maintenance_picking_views.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
    "application": False,
}
