ATSTI Odoo — Branch 18.0
Descrição

Este branch reúne os módulos personalizados da ATSTI para o Odoo 18.0, contemplando adaptações fiscais brasileiras, integrações, customizações de relatórios, automações, entre outros. Tem como objetivo prover funcionalidades específicas que não existem no Odoo padrão, para clientes no Brasil.
Licença

GPL-3.0 – Software livre.
GitHub
Estrutura

Pré-requisitos

    Odoo 18.0

    Python (versão compatível com Odoo 18)

    Dependências externas (bibliotecas de Python) de cada módulo (ex: para geração de NFE, XML, etc.)

    Acesso a serviços ou APIs que forem usados (por exemplo, SEFAZ, marketplaces, etc.)

Instalação

    Clone este repositório, ramo 18.0:

    git clone --branch 18.0 https://github.com/ATSTI/ats-odoo.git

    Copie os módulos desejados para o diretório de add-ons/custom do seu Odoo, ou configure o caminho para incluir o diretório do repositório.

    Instale dependências externas (via pip) caso algum módulo exija bibliotecas adicionais.

    Reinicie o servidor Odoo.

    No Odoo, ative o modo de desenvolvedor e vá até Apps → Atualizar lista de apps.

    Instale os módulos desejados via interface.

Como contribuir

    Abra issues para reportar bugs ou sugerir melhorias.

    Use pull requests apontando para o branch 18.0.

    Escreva testes se possível, especialmente para integrações fiscais ou que envolvem lógica de negócio sensível.

    Mantenha compatibilidade com padrões do Odoo.

Boas práticas

    Versionamento: ao modificar módulos, incremente versões nos arquivos __manifest__.py.

    Documentação: descreva bem os campos novos, modelos modificados, e o impacto em processos como faturamento, impostos, etc.

    Backup: sempre fazer backup dos dados antes de implantar módulos com impacto fiscal ou contábil.

Contato

Para dúvidas ou suporte:

    ATSTi Soluções

    ats@atsti.com.br

    +55 19 99684-8519
    
