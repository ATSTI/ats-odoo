import json

from psycopg2 import IntegrityError

from odoo.addons.website.controllers.form import WebsiteForm
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessDenied, ValidationError, UserError
from odoo.tools.misc import hmac, consteq
from odoo.tools.translate import _

from erpbrasil.base.misc import punctuation_rm
from werkzeug.exceptions import BadRequest

class WebsiteFormOverride(WebsiteForm):

    @http.route(
        '/website/form/<string:model_name>',
        type='http',
        auth="public",
        methods=['POST'],
        website=True,
        csrf=False
    )
    def website_form(self, model_name, **kwargs):
        csrf_token = request.params.pop('csrf_token', None)
        if request.session.uid and not request.validate_csrf(csrf_token):
            raise BadRequest('Session expired (invalid CSRF token)')

        try:
            with request.env.cr.savepoint():


                if request.env['ir.http']._verify_request_recaptcha_token('website_form'):
                    kwargs = dict(request.params)
                    kwargs.pop('model_name')
                    return self._handle_website_form(model_name, **kwargs)

            error = _("Suspicious activity detected by Google reCaptcha.")

        except (ValidationError, UserError) as e:
            error = e.args[0]

        return json.dumps({
            'error': error,
        })
    
    def _handle_website_form(self, model_name, **kwargs):
        model_record = request.env['ir.model'].sudo().search([('model', '=', model_name), ('website_form_access', '=', True)])
        if not model_record:
            return json.dumps({
                'error': _("The form's specified model does not exist")
            })

        try:
            data = self.extract_data(model_record, kwargs)
        # If we encounter an issue while extracting data
        except ValidationError as e:
            # I couldn't find a cleaner way to pass data to an exception
            return json.dumps({'error_fields': e.args[0]})

        try:
            if data['record']['vat'] and model_name == 'res.partner':
                partner = request.env['res.partner'].sudo().search([('cnpj_cpf_stripped', '=', punctuation_rm(data['record']['vat']))], limit=1)
                if 'consulta' in data['custom'].split() and 'Yes' in data['custom'].split():
                    if not partner:
                        raise AccessDenied("Parceiro não encontrado. Verifique o CNPJ/CPF informado.")
                if partner:
                    values = data['record']
                    values.pop('name')
                    values.pop('vat')  # We don't want to update the name and vat of an existing partner
                    if values:
                        partner.sudo().write(values)
                    id_record = partner.id
                else:
                    id_record = self.insert_record(request, model_record, data['record'], data['custom'], data.get('meta'))
            else:
                id_record = self.insert_record(request, model_record, data['record'], data['custom'], data.get('meta'))
            if id_record:
                self.insert_attachment(model_record, id_record, data['attachments'])
                # in case of an email, we want to send it immediately instead of waiting
                # for the email queue to process
                if model_name == 'mail.mail':
                    form_has_email_cc = {'email_cc', 'email_bcc'} & kwargs.keys() or \
                        'email_cc' in kwargs["website_form_signature"]
                    # remove the email_cc information from the signature
                    kwargs["website_form_signature"] = kwargs["website_form_signature"].split(':')[0]
                    if kwargs.get("email_to"):
                        value = kwargs['email_to'] + (':email_cc' if form_has_email_cc else '')
                        hash_value = hmac(model_record.env, 'website_form_signature', value)
                        if not consteq(kwargs["website_form_signature"], hash_value):
                            raise AccessDenied('invalid website_form_signature')
                    request.env[model_name].sudo().browse(id_record).send()

        # Some fields have additional SQL constraints that we can't check generically
        # Ex: crm.lead.probability which is a float between 0 and 1
        # TODO: How to get the name of the erroneous field ?
        except IntegrityError:
            return json.dumps(False)

        request.session['form_builder_model_model'] = model_record.model
        request.session['form_builder_model'] = model_record.name
        request.session['form_builder_id'] = id_record

        return json.dumps({'id': id_record})