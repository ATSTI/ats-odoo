
Este modulo cria um cron para notificação de vencimento dos certificados

Uso
===

Criado um cron "Lembrete de vencimento do certificado", nele é possivel administrar duas datas:
-vencimento = A primeira é quantos dias você quer ser lembrado antes de vencer o certificado;
-intervalo = O segundo é o intervalo, que tem interferencia direto nas notificações que vão aparecer;
    Exemplo: vencimento = 30 , intervalo = 5
        Caso o certificado vença em mais de 30 dias não aparece nada; 30 dias = intervalo x 6
        Faltando 25 dias para vencer, irá aparecer uma notificação de informação; intervalo x 5
        Faltando 5 dias ou menos irá aparecer um alerta de perigo para renovação; intervalo


