odoo.define('pdv_fiado.nfce_dest_patch', function (require) {
    "use strict";

    const NFeModule = require('l10n_br_pos_nfce.nfe-xml');
    const NFeXML = NFeModule.NFeXML;

    const _super = NFeXML.prototype.mountDestinataryTag;

    NFeXML.prototype.mountDestinataryTag = function () {

        const client = this.order.get_client();
        const NFCeEnvironment = this.pos.config.nfce_environment;

        // CPF vindo do seu botão
        const cpfFromButton =
            (this.order.get_extra_note && this.order.get_extra_note()) || '';

        const cleanedCPF = cpfFromButton.replace(/\D/g, '');

        // prioridade → CPF digitado
        if (cleanedCPF.length === 11) {
            return {
                CPF: cleanedCPF,
                xNome: NFCeEnvironment === "2"
                    ? "NF-E EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL"
                    : (client?.name || "CONSUMIDOR"),
                indIEDest: "9",
            };
        }

        // fallback → comportamento original
        return _super.apply(this, arguments);
    };

});
