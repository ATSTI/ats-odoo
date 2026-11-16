{
    "name": "Website FSM Orders",
    "summary": "Exibe informações das FSM orders do usuário logado no site",
    "version": "14.0.1.0.0",
    "category": "Marketing",
    "author": "ATS Soluções",
    "license": "AGPL-3",
    "depends": ["website", "fieldservice"],
    "assets": {
        "web.assets_frontend": [
            "website_fsm_orders/static/src/js/OrdersDashboard.js",
        ],
    },
    "data": [
        "views/templates.xml",
    ],
    "installable": True,
    "application": False,
}
