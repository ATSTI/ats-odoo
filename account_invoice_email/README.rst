
Este modulo envia email de Vencimento de Fatura e Aviso de vencimento

Uso
===

Alterar na linha do CRON, o dia_vencimento, e o tipo do email:
   
   cron_email_fatura_cobranca(dia_vcto=5, tipo_email="VCTO")


   dia_vcto = Número de dias que o email será enviado ANTES do vencimento ou data que a fatura foi CRIADA, 

       exemplo: O Vencimento é dia 12 quero que o email vá dois dias ANTES, então o dia_vcto = 2

       exemplo 2: Enviando todas as faturas criadas na semana, programa o CRON para Sexta-feira, e usa dia_vcto = -5

   tipo_email = Usar VCTO para template : 'Fatura: Cobranca'
                Usar CRIADA para template : 'Fatura: Cobranca', busca a faturas criadas
                Usar AVISO para template : 'Fatura: aviso vencimento'

Email : 
    será criado dois modelos :
       - Fatura: Cobranca
       - Fatura: aviso vencimento

