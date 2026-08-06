ATSTI Odoo — Branch 18.0
Descrição

Branch de funcionamento dos módulos da Empresa Especifica, devido a não conversão do módulo l10n_br_account (novembro de 2025) através desse branch fiz a conversão por jeitos mais simples e menos funcionais que o pessoal da localização. Quando migrarem esse branch não terá mais função

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
    
