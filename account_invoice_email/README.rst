
Este modulo envia email de Vencimento de Fatura e Aviso de vencimento

Uso
===

Alterar na linha do CRON, o dia_vencimento, e o tipo do email:
   
   cron_email_fatura_cobranca(dia_vcto=5, tipo_email="VCTO")


   dia_vcto = Número de dias que o email será enviado ANTES do vencimento, 
       exemplo: O Vencimento é dia 12 quero que o email vá dois dias ANTES, então o dia_vcto = 2

   tipo_email = Usar VCTO para template : 'Fatura: Cobranca'
                Usar AVISO para template : 'Fatura: aviso vencimento'

