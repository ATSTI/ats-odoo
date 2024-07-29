# Copyright 2023 Emanuel Cino
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Point of Sale - Partner contact Credit limit",
    "summary": "Adds the credit limit in the customer screen of POS",
    "version": "14.0.1.0.2",
    "development_status": "Beta",
    "category": "Point of sale",
    "website": "https://github.com/OCA/pos",
    "author": "Emanuel Cino, Odoo Community Association (OCA)",
    "maintainers": ["ecino"],
    "license": "AGPL-3",
    "installable": True,
    "depends": ["point_of_sale", "om_credit_limit"],
    "data": ["views/assets.xml"],
    "qweb": [
        "static/src/xml/ClientDetailsEdit.xml",
    ],
}
