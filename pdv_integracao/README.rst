================================
INTEGRACAO PDV(Lazarus) com ODOO
================================



Configuração do PDV (conf.ini):
    odoo_user := conf.ReadString('SISTEMA', 'User', '');  ->  Usuário e Ponto de Venda PRECISA ser o mesmo nome.
    odoo_acesso := conf.ReadString('SISTEMA', 'Acesso', '');
    
Configuração ODOO:
   Adicionar em Parametros do Sistema:
       Diários de Contas a Receber :
       Name:  pos.diario_contas
       Value: [1,2]  (exemplo: diario 1 e 2)


Authors
~~~~~~~

* ATSTi Soluções

Contributors
~~~~~~~~~~~~

* Carlos Silveira <carlos@atsti.com.br>
* Manoel dos Santos <manoel@atsti.com.br>

