# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ChatwootComposer(models.TransientModel):
    _name = 'chatwoot.composer'
    _description = 'Chatwoot Composer'

    partner_id = fields.Many2many(
        comodel_name='res.partner',
        string='Destinatários',
        required=True
    )
    template_id = fields.Many2one(
        'chatwoot.message.template', 
        string="Template"
    )
    body = fields.Text(
        string="Mensagem a ser enviada", 
        required=True
    )
    chatwoot_id = fields.Many2one(
        'chatwoot.instance', 
        string="Instância", 
        domain=[('account_id', '=', "1")],
    )
    attachment_ids = fields.Many2many(
        'ir.attachment', 
        string="Anexos"
    )
    preview_html = fields.Html(
        string="Preview da Mensagem",
        compute="_compute_preview",
        sanitize=True
    )

    model = fields.Char('Related Document Model')
    res_id = fields.Integer('Related Document ID')

    @api.model
    def default_get(self, fields):
        res = super(ChatwootComposer, self).default_get(fields)

        if self.env.context.get('active_model') and self.env.context.get('active_id'):
            res['model'] = self.env.context['active_model']
            res['res_id'] = self.env.context['active_id']
            record = self.env[res['model']].browse(res['res_id'])
            if hasattr(record, 'partner_id') and record.partner_id:
                partner_ids = record.partner_id.ids
                res['partner_id'] = [(6, 0, partner_ids)]

        instance = self.env['chatwoot.instance'].search([('account_id', '=', '1')], limit=1)
        if instance:
            res['chatwoot_id'] = instance.id

        return res

    @api.depends('body', 'attachment_ids')
    def _compute_preview(self):
        for record in self:
            preview = ""
            if record.body:
                preview += record.body.replace("\n", "<br/>")
            if record.attachment_ids:
                for att in record.attachment_ids:
                    if att.mimetype and att.mimetype.startswith("image/"):
                        preview += f'<br/><img src="data:{att.mimetype};base64,{att.datas.decode()}" ' \
                                f'style="max-width:200px; max-height:200px; margin:5px;"/>'
                    else:
                        preview += f'<br/><a href="/web/content/{att.id}?download=true">{att.name}</a>'
            if not preview:
                preview = "<i>O Preview aparecerá aqui..</i>"

            record.preview_html = preview



    @api.onchange('template_id')
    def _onchange_template_id(self):
        """Preenche a mensagem automaticamente ao selecionar um template"""
        if self.template_id:
            self.body = self.template_id.body
            if self.template_id.attachment_ids:
                self.attachment_ids = [(6, 0, self.template_id.attachment_ids.ids)]
            else:
                self.attachment_ids = [(5, 0, 0)]  # remove anexos caso template não tenha

    def action_send_message(self):
        self.ensure_one()
        if not self.body and not self.attachment_ids:
            raise UserError(_("Please enter a message or add an attachment."))

     
        record = self.env[self.model].browse(self.res_id) if self.model and self.res_id else None

        try:
            for partner in self.partner_id:
                phone_number = f"{partner.phone_sanitized}"
                conversation_id = self.chatwoot_id.create_new_conversation(phone_number, partner)
                if conversation_id:
                    conversation_id = conversation_id['id']
                else:
                    raise UserError(_("Failed to create conversation for %s") % partner.name)
                if self.attachment_ids:
                    first_attachment = self.attachment_ids[0]
                    self.chatwoot_id.send_chatwoot_attachment( 
                        conversation_id,
                        first_attachment,
                        message=self.body
                    )
                    for attachment in self.attachment_ids[1:]:
                        self.chatwoot_id.send_chatwoot_attachment(conversation_id, attachment)
                else:
                    self.chatwoot_id.send_text(conversation_id, self.body)

            if record:
                names = ', '.join(self.partner_id.mapped('name'))
                chatter_body = _("WhatsApp message sent to %s:\n%s") % (names, self.body)
                record.message_post(
                    body=chatter_body,
                    message_type='comment',
                    subtype_xmlid='mail.mt_note',
                    attachment_ids=self.attachment_ids.ids
                )

        except Exception as e:
            raise UserError(_("Failed to send WhatsApp message: %s") % e)

        return {'type': 'ir.actions.act_window_close'}
