# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
#        (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, exceptions, fields, models, tools


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.multi
    def _message_auto_subscribe_notify(self, partner_ids):
        """ Notify newly subscribed followers of the last posted message.
            :param partner_ids : the list of partner to add as needaction partner of the last message
                                 (This excludes the current partner)
        """
        if self._name in ('account.invoice', 'sale.order'):
            return
        if not partner_ids:
            return
        for record in self:
            record.message_post_with_view(
                'mail.message_user_assigned',
                composition_mode='mass_mail',
                partner_ids=[(4, pid) for pid in partner_ids],
                auto_delete=True,
                auto_delete_message=True,
                subtype_id=self.env.ref('mail.mt_note').id)
