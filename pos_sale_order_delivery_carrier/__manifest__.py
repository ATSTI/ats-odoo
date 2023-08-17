{
    "name": "POS Sale Order Delivery Carrier",
    "version": "14.0.1.0.0",
    "category": "Sales/Point of Sale",
    "summary": "POS Sale Order Delivery Carrier",
    "depends": ["pos_order_to_sale_order", "delivery"],
    "website": "https://github.com/OCA/pos",
    "author": "Cetmix,Odoo Community Association (OCA)",
    "maintainers": ["GabbasovDinar", "CetmixGitDrone"],
    "data": [
        "views/delivery_carrier_view.xml",
        "views/res_config_settings_view.xml",
    ],
    "installable": True,
    "assets": {
        "point_of_sale.assets": [
            "pos_sale_order_delivery_carrier/static/src/css/pos.css",
            "pos_sale_order_delivery_carrier/static/src/js/**/*.js",
            "pos_sale_order_delivery_carrier/static/src/xml/**/*.xml",
        ],
    },
    "license": "AGPL-3",
}
