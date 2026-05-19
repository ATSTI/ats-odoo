# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import TransactionCase

from odoo.addons.attachment_zipped_download.tests.test_attachment_zipped_download import (
    TestAttachmentZippedDownloadBase,
)


class TestInvoiceAttachmentZippedDownload(
    TransactionCase, TestAttachmentZippedDownloadBase
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.account_a = cls.env["account.move"].create({"name": "Test account A"})
        cls.account_b = cls.env["account.move"].create({"name": "Test account B"})
        cls.account_c = cls.env["account.move"].create({"name": "Test account C"})
        cls.attachment_a = cls._create_attachment(
            cls.env,
            cls.env.uid,
            "account-a.txt",
            model=cls.account_a._name,
            res_id=cls.account_a.id,
        )
        cls.attachment_b = cls._create_attachment(
            cls.env,
            cls.env.uid,
            "account-b.txt",
            model=cls.account_b._name,
            res_id=cls.account_b.id,
        )
        cls.attachment_b_extra = cls._create_attachment(
            cls.env,
            cls.env.uid,
            "account-template-b.txt",
            model=cls.account_b.account_tmpl_id._name,
            res_id=cls.account_b.account_tmpl_id.id,
        )

    def test_action_download_attachments_no_attachment(self):
        action = self.account_c.account_tmpl_id.action_download_attachments()
        self.assertEqual(action["type"], "ir.actions.client")
        self.assertEqual(action["tag"], "display_notification")
        action = self.account_c.action_download_attachments()
        self.assertEqual(action["type"], "ir.actions.client")
        self.assertEqual(action["tag"], "display_notification")

    def test_action_download_attachments_one_attachment_1(self):
        action = self.account_a.account_tmpl_id.action_download_attachments()
        self.assertEqual(action["type"], "ir.actions.act_url")
        self.assertEqual(action["target"], "self")
        self.assertEqual(
            action["url"], "/web/content/%s?download=1" % self.attachment_a.id
        )
        action = self.account_a.action_download_attachments()
        self.assertEqual(action["type"], "ir.actions.act_url")
        self.assertEqual(action["target"], "self")
        self.assertEqual(
            action["url"], "/web/content/%s?download=1" % self.attachment_a.id
        )

    def test_action_download_attachments_one_attachment_2(self):
        action = self.account_b.account_tmpl_id.action_download_attachments()
        self.assertEqual(action["type"], "ir.actions.act_url")
        self.assertEqual(action["target"], "self")
        self.assertTrue(action["url"].startswith("/web/attachment/download_zip?ids="))
        attachment_ids = sorted(map(int, action["url"].split("=")[1].split(",")))
        self.assertNotIn(self.attachment_a.id, attachment_ids)
        self.assertIn(self.attachment_b.id, attachment_ids)
        self.assertIn(self.attachment_b_extra.id, attachment_ids)
        action = self.account_b.action_download_attachments()
        self.assertEqual(action["type"], "ir.actions.act_url")
        self.assertEqual(action["target"], "self")
        self.assertTrue(action["url"].startswith("/web/attachment/download_zip?ids="))
        attachment_ids = sorted(map(int, action["url"].split("=")[1].split(",")))
        self.assertNotIn(self.attachment_a.id, attachment_ids)
        self.assertIn(self.attachment_b.id, attachment_ids)
        self.assertIn(self.attachment_b_extra.id, attachment_ids)

    def test_action_download_attachments_multi_attachment(self):
        accounts = self.account_a + self.account_b + self.account_c
        account_templates = accounts.mapped("account_tmpl_id")
        action = account_templates.action_download_attachments()
        self.assertEqual(action["type"], "ir.actions.act_url")
        self.assertEqual(action["target"], "self")
        self.assertTrue(action["url"].startswith("/web/attachment/download_zip?ids="))
        attachment_ids = sorted(map(int, action["url"].split("=")[1].split(",")))
        self.assertIn(self.attachment_a.id, attachment_ids)
        self.assertIn(self.attachment_b.id, attachment_ids)
        self.assertIn(self.attachment_b_extra.id, attachment_ids)
        action = accounts.action_download_attachments()
        self.assertEqual(action["type"], "ir.actions.act_url")
        self.assertEqual(action["target"], "self")
        self.assertTrue(action["url"].startswith("/web/attachment/download_zip?ids="))
        attachment_ids = sorted(map(int, action["url"].split("=")[1].split(",")))
        self.assertIn(self.attachment_a.id, attachment_ids)
        self.assertIn(self.attachment_b.id, attachment_ids)
        self.assertIn(self.attachment_b_extra.id, attachment_ids)
