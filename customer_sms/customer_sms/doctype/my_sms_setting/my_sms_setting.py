# Copyright (c) 2025, md and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MYSMSSetting(Document):
    def validate(self):
        pass

        # # Example: Prevent changing 'customer_site' after creation
        # if self.get_doc_before_save():
        #     old_value = self.get_doc_before_save().sms_sent_today
        #     if self.sms_sent_today != old_value:
        #         frappe.throw("SMS Sent Today cannot be modified!")
