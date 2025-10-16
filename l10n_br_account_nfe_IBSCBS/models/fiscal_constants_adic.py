from odoo.addons.l10n_br_fiscal.constants import fiscal as constants

# Adicionando os novos domínios à lista TAX_DOMAIN
TAX_DOMAIN_IBS = "ibs"
TAX_DOMAIN_CBS = "cbs"
TAX_DOMAIN_IBSCBS = "ibscbs"
TAX_DOMAIN_IBSUF = "ibsuf"
TAX_DOMAIN_IBSMUN = "ibsmun"

# Adicionando à lista original TAX_DOMAIN
constants.TAX_DOMAIN += [
    (TAX_DOMAIN_IBS, "IBS"),
    (TAX_DOMAIN_CBS, "CBS"),
    (TAX_DOMAIN_IBSCBS, "IBSCBS"),
    (TAX_DOMAIN_IBSUF, "IBSUF"),
    (TAX_DOMAIN_IBSMUN, "IBSMun"),
]