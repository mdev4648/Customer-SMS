import frappe, requests
from frappe.utils import now


@frappe.whitelist()
def sync_sms_logs():
    """
    Sync SMS logs from central server and notify users if any SMS failed.
    """
    settings = frappe.get_single("MY SMS Setting")  # client config
    central_url = settings.central_api_url
    api_key = settings.api_key
    customer_site = frappe.local.site

    try:
        res = requests.get(
            f"{central_url}/api/method/haron_sms_gateway.api.get_sms_logs",
            params={"api_key": api_key, "customer_site": customer_site},
            timeout=10,
        )
        data = res.json()
        failed_logs = []

        if "message" in data:
            for log in data["message"]:
                # Check if log exists locally
                if frappe.db.exists("Client SMS Log", {"log_id": log["name"]}):
                    local_log = frappe.get_doc(
                        "Client SMS Log", {"log_id": log["name"]}
                    )

                    # Update only if status changed
                    if local_log.status != log["status"]:
                        prev_status = local_log.status
                        local_log.phone = log["phone"]
                        local_log.message = log["message"]
                        local_log.status = log["status"]
                        local_log.creation_time = log["creation"]
                        local_log.save(ignore_permissions=True)

                        # If it just became Failed, add to alert
                        if prev_status != "Failed" and log["status"] == "Failed":
                            failed_logs.append(local_log)

                else:
                    # Insert new logs anyway
                    doc = frappe.get_doc(
                        {
                            "doctype": "Client SMS Log",
                            "log_id": log["name"],
                            "phone": log["phone"],
                            "message": log["message"],
                            "status": log["status"],
                            "creation_time": log["creation"],
                        }
                    )
                    doc.insert(ignore_permissions=True)

                    if log["status"] == "Failed":
                        failed_logs.append(doc)

            frappe.db.commit()

        # Create notifications for failed logs
        for failed in failed_logs:
            frappe.get_doc(
                {
                    "doctype": "Notification Log",
                    "subject": f"SMS Failed to {failed.phone}",
                    "email_content": f"Message: {failed.message}",
                    "for_user": "Administrator",  # or loop through actual users
                    "type": "Alert",
                    "document_type": failed.doctype,
                    "document_name": failed.name,
                    "seen": 0,
                }
            ).insert(ignore_permissions=True)

        frappe.db.commit()

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Sync SMS Logs Failed")
