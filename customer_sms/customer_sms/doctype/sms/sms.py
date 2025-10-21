# Copyright (c) 2025, md and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class sms(Document):
    def on_submit(self):
        if not self.sender_name:
            frappe.throw("Sender Name is required")
