{
    "name": "POS Fiado Button",
    "version": "14.0.1.0.0",
    "summary": "Adiciona um botão Fiado na tela de pagamento do POS",
    "description": """
        Este módulo adiciona um botão chamado 'Fiado' na tela de pagamento do POS
        que permite alternar o status de faturamento do pedido (toggleIsFiado).
    """,
    "category": "Point of Sale",
    "author": "Você",
    "website": "https://seusite.com",
    "license": "AGPL-3",
    "depends": ["point_of_sale"],
    "data": [
        "views/assets.xml",             # Assets para JS e CSS
        # "views/pos_custom_button.xml",  # XML do botão no template do POS
    ],
    "qweb": [],
    "installable": True,
    "application": False,
    "auto_install": False
}
