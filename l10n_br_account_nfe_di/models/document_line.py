from odoo.addons.spec_driven_model.models import spec_models


class NFeLine(spec_models.StackedModel):
    _name = "l10n_br_fiscal.document.line"
    _inherit = ["l10n_br_fiscal.document.line", "nfe.40.det"]
    _stacked = "nfe.40.det"
    _field_prefix = "nfe40_"
    _schema_name = "nfe"
    _schema_version = "4.0.0"
    _odoo_module = "l10n_br_nfe"
    _spec_module = "odoo.addons.l10n_br_nfe_spec.models.v4_00.leiauteNFe"
    _spec_tab_name = "NFe"
    _stack_skip = "nfe40_det_infNFe_id"
    _stacking_points = {}
    _force_stack_paths = ("det.imposto",)

    def _export_fields(self, xsd_fields, class_obj, export_dict):
        if class_obj._name == "nfe.40.prod":
            # import pudb;pu.db
            for aml in self.account_line_ids:
                if aml.move_id.move_type == "in_invoice":
                    for di in aml.di_ids:
                        vals_di_di = {
                            "nfe40_DI_prod_id": di.id,
                            "nfe40_nDI" : di.name,
                            "nfe40_dDI" : di.date_registration,
                            "nfe40_xLocDesemb" : di.location,
                            "nfe40_UFDesemb" : di.state_id.code,
                            "nfe40_dDesemb": di.date_release,
                            "nfe40_tpViaTransp" : di.type_transportation,
                            "nfe40_vAFRMM" : di.afrmm_value,
                            "nfe40_tpIntermedio" : di.tpIntermedio,
                            "nfe40_CNPJ" : di.thirdparty_cnpj,
                            "nfe40_UFTerceiro" : di.thirdparty_state_id.code,
                            "nfe40_cExportador" : di.exporting_code,
                        }
                    
                        list_adi = []
                        for line in di.adi_ids:
                            vals_adi = {
                                "nfe40_nAdicao": line.name,
                                "nfe40_nSeqAdic": line.sequence_di,
                                "nfe40_cFabricante": line.manufacturer_code,
                                "nfe40_vDescDI": "{:.2f}".format(line.amount_discount) if line.amount_discount != 0.0 else False,
                                "nfe40_nDraw": line.drawback_number,
                            }
                            obj = self.env["nfe.40.adi"].create(vals_adi)
                            list_adi.append(obj.id)
                        if len(list_adi):
                            vals_di_di["nfe40_adi"] = [(6, 0, list_adi)]                       
                            obj_di = self.env["nfe.40.di"].create(vals_di_di).id
                            self.nfe40_DI = [(6, 0, [obj_di])]

            if self.account_line_ids.move_id.move_type == "out_invoice":
                vals_detexp = []
                for det in self.exp_ids:
                    vals_det_exp = {
                        "nfe40_detExport_prod_id": det.id,
                        "nfe40_nDraw": det.name
                    }
                    vals_detexp = {
                        "nfe40_nRE": det.registro_exp,
                        "nfe40_chNFe": det.chava_nfe,
                        "nfe40_qExport": "{:.2f}".format(det.q_export) if det.q_export != 0.0 else False,
                    }
                # TODO estou gravando so uma linha , se tiver mais vai dar erro
                if len(vals_detexp):
                    export_id = self.env["nfe.40.exportind"].create(vals_detexp)
                    vals_det_exp["nfe40_exportInd"] = export_id.id                       
                    obj_di = self.env["nfe.40.detexport"].create(vals_det_exp).id
                    self.nfe40_detExport = [(6, 0, [obj_di])]

        return super()._export_fields(xsd_fields, class_obj, export_dict)