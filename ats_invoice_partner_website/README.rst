Invoice Partner Website (Odoo 14)

Este módulo (estilo OCA) copia o campo **Website** do parceiro para um campo somente-leitura nas faturas de cliente
(*account.move* com *move_type* = out_invoice/out_refund).

Comportamento
-------------
- Ao criar/editar uma fatura e selecionar o cliente, o campo é preenchido automaticamente.
- No *create()* também é preenchido para cobrir importações ou criações via código (sem UI).
- Não tenta atualizar faturas antigas: o valor é copiado no momento da criação/seleção e fica congelado.

Instalação
----------
- Coloque a pasta `ats_invoice_partner_website` no seu *addons path*.
- Atualize a lista de apps e instale o módulo.

Licença: AGPL-3.