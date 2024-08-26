# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

def post_init_hook(cr, registry):
    """Copiar campos br_base Trust."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    import pudb;pu.db
    partner = env["res.partner"].search([], order="ibge_code")
    city = 0
    city_id = 0
    for prt in partner:
        if prt.city_id or not prt.ibge_code:
            continue
        if not prt.city_id and city != prt.ibge_code:
            city_id = env["res.city"].search([("ibge_code", "like", prt.ibge_code)])
            for ct in city_id:
                if ct.state_id.code == prt.state_id.code:
                    city = prt.ibge_code
                    city_id = ct.id
        if city_id:
            prt.city_id = city_id
        # prt.ibge_code = prt.city_id.ibge_code
        prt.cnpj_cpf = prt.cnpj_cpf_bkp
        prt.inscr_est = prt.inscr_est_bkp
        # prt.rg_fisica = prt.rg_fisica_bkp
        prt.inscr_mun = prt.inscr_mun_bkp
        prt.suframa = prt.suframa_bkp
        prt.legal_name = prt.legal_name_bkp
        prt.district = prt.district_bkp
        prt.street_number = prt.number_bkp
        if prt.indicador_ie_dest_bkp:
            prt.ind_ie_dest = prt.indicador_ie_dest_bkp
            if prt.indicador_ie_dest_bkp == "9":
                prt.ind_final = "1"

    import pudb;pu.db
    product = env["product.template"].search([], order = "ncm")
    ncm = '0'
    ncm_id = 0
    for prd in product:
        if prd.ncm_id or not prd.ncm:
            continue
        if prd.ncm != ncm:
            ncm_id = env["l10n_br_fiscal.ncm"].search(["code", "=", prd.ncm])
            ncm = prd.code
        if ncm_id:
            prd.ncm_id = ncm_id.id
        prd.type_product = prd.type_bkp
        prd.fiscal_type = prd.fiscal_type_bkp
        prd.origin = prd.origin_bkp
        if prd.code_servico:
            prd.type = "service"
            service_id = env["l10n_br_fiscal.service.type"].search(["code", "=", prd.code_servico])
            if service_id:
                prd.service_type_id = service_id.id

    # cr.execute(
    #     """
    #         insert into br_odoo_nfe (select 
	# 					 id, code, name, company_id, state, schedule_user_id, tipo_operacao, model, serie, serie_documento, 
	# 					 numero, numero_controle, data_agendada, data_emissao, data_autorizacao, data_fatura, ambiente, 
	# 					 finalidade_emissao, invoice_id, partner_id, commercial_partner_id, partner_shipping_id, payment_term_id, 
	# 					 fiscal_position_id, valor_bruto, valor_frete, valor_seguro, valor_desconto, valor_despesas, valor_bc_icms, 
	# 					 valor_icms, valor_icms_deson, valor_bc_icmsst, valor_icmsst, valor_ii, valor_ipi, valor_pis, valor_cofins,
	# 					 valor_estimado_tributos, valor_servicos, valor_bc_issqn, valor_issqn, valor_pis_servicos, valor_cofins_servicos, 
	# 					 valor_retencao_issqn, valor_retencao_pis, valor_retencao_cofins, valor_bc_irrf, valor_retencao_irrf, valor_bc_csll, 
	# 					 valor_retencao_csll, valor_bc_inss, valor_retencao_inss, valor_final, informacoes_legais, informacoes_complementares,
	# 					 codigo_retorno, mensagem_retorno, numero_nfe, xml_to_send, xml_to_send_name, email_sent, payment_mode_id, iest,
	# 					 ambiente_nfe, ind_final, ind_pres, ind_dest, ind_ie_dest, tipo_emissao, data_entrada_saida, modalidade_frete,
	# 					 transportadora_id, placa_veiculo, uf_veiculo, rntc, uf_saida_pais_id, local_embarque, local_despacho, numero_fatura,
	# 					 fatura_bruto, fatura_desconto, fatura_liquido, nota_empenho, pedido_compra, contrato_compra, sequencial_evento, recibo_nfe,
	# 					 chave_nfe, protocolo_nfe, nfe_processada, nfe_processada_name, valor_icms_uf_remet, valor_icms_uf_dest, valor_icms_fcp_uf_dest,
	# 					 qrcode_hash, qrcode_url, metodo_pagamento, valor_pago, troco, create_uid, create_date, write_uid, write_date
	# 					 from invoice_eletronic);
    #         """
    # )

    # cr.execute(
    #     """
    #         insert into br_odoo_nfe_item (select 
    #             id, name, company_id, invoice_eletronic_id, product_id, tipo_produto, cfop, ncm, uom_id, quantidade, preco_unitario, pedido_compra,
    #             item_pedido_compra, frete, seguro, desconto, outras_despesas, tributos_estimados, valor_bruto, valor_liquido, indicador_total, origem, icms_cst,
    #             icms_aliquota, icms_tipo_base, icms_base_calculo, icms_aliquota_reducao_base, icms_valor, icms_valor_credito, icms_aliquota_credito, icms_st_tipo_base,
    #             icms_st_aliquota_mva, icms_st_aliquota, icms_st_base_calculo, icms_st_aliquota_reducao_base, icms_st_valor, icms_aliquota_diferimento, icms_valor_diferido, 
    #             icms_motivo_desoneracao, icms_valor_desonerado, ipi_cst, ipi_aliquota, ipi_base_calculo, ipi_reducao_bc, ipi_valor, ii_base_calculo, ii_aliquota,
    #             ii_valor_despesas, ii_valor, ii_valor_iof, pis_cst, pis_aliquota, pis_base_calculo, pis_valor, pis_valor_retencao, cofins_cst, cofins_aliquota,
    #             cofins_base_calculo, cofins_valor, cofins_valor_retencao, issqn_codigo, issqn_aliquota, issqn_base_calculo, issqn_valor, issqn_valor_retencao, 
    #             csll_base_calculo, csll_aliquota, csll_valor_retencao, irrf_base_calculo, irrf_aliquota, irrf_valor_retencao, inss_base_calculo, inss_aliquota,
    #             inss_valor_retencao, account_invoice_line_id, cest, classe_enquadramento_ipi, codigo_enquadramento_ipi,
    #             tem_difal, icms_bc_uf_dest, icms_aliquota_fcp_uf_dest, icms_aliquota_uf_dest, icms_aliquota_interestadual, icms_aliquota_inter_part, icms_uf_remet,
    #             icms_uf_dest, icms_fcp_uf_dest, informacao_adicional, icms_substituto, icms_bc_st_retido, icms_aliquota_st_retido, icms_st_retido
    #     	FROM invoice_eletronic_item);
    #     """
    # )


# access_nfe_reboque_manager,access_nfe_reboque,model_nfe_reboque,account.group_account_manager,1,1,1,1
# access_nfe_volume_manager,access_nfe_volume,model_nfe_volume,account.group_account_manager,1,1,1,1
# access_nfe_duplicata_manager,access_nfe_duplicata,model_nfe_duplicata,account.group_account_manager,1,1,1,1
# access_nfe_reboque_accountant,access_nfe_reboque,model_nfe_reboque,account.group_account_user,1,1,1,0
# access_nfe_volume_accountant,access_nfe_volume,model_nfe_volume,account.group_account_user,1,1,1,0
# access_nfe_duplicata_accountant,access_nfe_duplicata,model_nfe_duplicata,account.group_account_user,1,1,1,0
# access_nfe_reboque_item_user,access_nfe_reboque,model_nfe_reboque,account.group_account_invoice,1,0,1,0
# access_nfe_volume_user,access_nfe_volume,model_nfe_volume,account.group_account_invoice,1,0,1,0
# access_nfe_duplicata_user,access_nfe_duplicata,model_nfe_duplicata,account.group_account_invoice,1,0,1,0
# access_invoice_eletronic_event_user,access_invoice_eletronic_event,model_br_odoo_nfe_event,account.group_account_invoice,1,0,1,0
# access_invoice_eletronic_event_accountant,access_invoice_eletronic_event,model_br_odoo_nfe_event,account.group_account_user,1,1,1,0
# access_invoice_eletronic_event_manager,access_invoice_eletronic_event,model_br_odoo_nfe_event,account.group_account_manager,1,1,1,1
