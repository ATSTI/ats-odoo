# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Invoice - Email ",
    "version": "14.0.0.0.0",
    "category": "Contract Management",
    "license": "AGPL-3",
    "author": "ATSTi Soluções",
    "website": "",
    "depends": ["l10n_br_account"],
    "development_status": "Production/Stable",
    "data": [
        "data/mail_template.xml",
        "data/account_email_cron.xml",
        "views/account_move.xml",
    ],
    "installable": True,
}
