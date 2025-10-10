import frappe
import requests
import json
from frappe.utils.background_jobs import enqueue
import re
import time


@frappe.whitelist()
def send_sms_on_submit(doc, method):
    phone = doc.phone
    message = doc.message

    if not phone or not message:
        frappe.throw("Phone and message are required to send SMS.")

    settings = frappe.get_single("MY SMS Setting")
    CENTRAL_SMS_API = settings.central_api_url
    CENTRAL_API_KEY = settings.api_key

    url = f"{CENTRAL_SMS_API}/api/method/haron_sms_gateway.api.send_sms_from_central"

    payload = {
        "phone": phone,
        "message": message,
        "api_key": CENTRAL_API_KEY,
        "customer_site": frappe.local.site,
        "callback_url": f"{frappe.utils.get_url()}/api/method/customer_sms.api.update_sms_status",
        "sender_name": settings.sender_name,
    }

    headers = {"Content-Type": "application/json"}

    try:
        res = requests.post(url, json=payload, headers=headers, timeout=10)

        # If central returns non-200, extract clean error
        if res.status_code != 200:
            try:
                error_json = res.json()
                msg = "SMS Sending Failed"

                # --- unwrap frappe _server_messages ---
                if "_server_messages" in error_json:
                    server_msgs = json.loads(error_json["_server_messages"])
                    if server_msgs:
                        inner = json.loads(server_msgs[0])
                        msg = inner.get("message", msg)

                # --- fallback to other fields ---
                elif "exception" in error_json:
                    msg = error_json.get("exception")
                elif "message" in error_json:
                    msg = error_json.get("message")

                # frappe.throw(msg)

            except Exception:

                frappe.throw("")

        # Success: unwrap response
        response_json = res.json()
        data = response_json.get("message", response_json)

        if data.get("status") == "queued":
            frappe.msgprint(f"SMS queued successfully for {phone}")
        else:
            frappe.throw(f"{data["message"]}")  # error message on submit

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "SMS Sending Failed")
        frappe.throw(str(e))


@frappe.whitelist()
def resend_sms(log_id):
    """Call Central Server's resend API to re-queue failed SMS from client"""
    log = frappe.get_doc("Client SMS Log", log_id)

    if log.status != "Failed":
        frappe.throw("Only Failed SMS can be resent")

    # Get settings
    settings = frappe.get_single("MY SMS Setting")
    CENTRAL_SERVER_URL = settings.central_api_url
    CENTRAL_API_KEY = settings.api_key

    central_resend_url = (
        f"{CENTRAL_SERVER_URL}/api/method/haron_sms_gateway.api.resend_sms"
    )

    try:
        res = requests.post(
            central_resend_url,
            data={
                "log_name": log.log_id,
                "api_key": CENTRAL_API_KEY,
                "customer_site": frappe.local.site,
            },
            timeout=10,
        )

        # Parse JSON safely
        try:
            response_json = res.json()
        except Exception:
            frappe.throw(res.text[:300] or "Central server returned non-JSON")

        # Unwrap Frappe API message if exists
        data = response_json.get("message", response_json)

        if data.get("status") == "queued":
            # Update client log
            log.status = "Queued"
            log.save(ignore_permissions=True)
            frappe.db.commit()

            frappe.msgprint(f"SMS re-queued successfully for {log.phone}")
            return {"status": "success", "msg": "SMS re-queued successfully"}
        else:
            # Real failure case
            msg = data.get("msg") or str(data)
            frappe.msgprint(f"Failed to re-queue SMS: {msg}")
            return {"status": "error", "msg": msg}

    except Exception as e:
        frappe.msgprint(f"Error while re-queuing SMS: {str(e)}")
        return {"status": "error", "msg": str(e)}


@frappe.whitelist(allow_guest=True)
def update_sms_status(
    log_id, status, phone=None, message=None, customer_site=None, sms_sent_today=None
):
    """
    Callback endpoint called by central server after processing.
    Create/update Client SMS Log and update Bulk SMS Result (if any).
    """

    # print(f"\n\n {log_id} {log.sms_count} \n\n\n\n\n\n\n")

    # Update or create Client SMS Log
    existing_log = frappe.db.exists("Client SMS Log", {"log_id": log_id})

    if existing_log:
        frappe.db.set_value("Client SMS Log", existing_log, "status", status)
    else:
        if not phone or not message:
            # Not enough info to create new client log
            # Return error but central may only retry; we stop quietly
            return {
                "status": "error",
                "msg": "Phone and message required to create new Client SMS Log",
            }

        doc = frappe.get_doc(
            {
                "doctype": "Client SMS Log",
                "log_id": log_id,
                "phone": phone,
                "message": message,
                "status": status,
                "customer_site": customer_site or frappe.local.site,
                "sms_sent_today": sms_sent_today or 0,
            }
        )
        doc.insert(ignore_permissions=True)

    frappe.db.commit()
    # update my sms setting

    try:
        sms_doc = frappe.get_single("MY SMS Setting")
        if sms_doc.api_key and sms_doc.central_api_url:
            api_url = f"{sms_doc.central_api_url}/api/method/haron_sms_gateway.api.get_api_key_info"
            params = {
                "api_key": sms_doc.api_key,
                "customer_site": sms_doc.customer_site or frappe.local.site,
            }

            res = requests.get(api_url, params=params, timeout=10)
            if res.status_code == 200 and res.json().get("message"):
                info = res.json()["message"]

                # --- Update fields directly ---
                sms_doc.valid_from = info.get("valid_from")
                sms_doc.valid_upto = info.get("valid_upto")
                sms_doc.status = info.get("status")
                sms_doc.daily_limit = info.get("daily_limit")
                sms_doc.sms_sent_today = info.get("sms_sent_today")
                sms_doc.remaining = info.get("remaining")

                sms_doc.save(ignore_permissions=True)
                frappe.db.commit()

                frappe.logger().info("MY SMS Setting auto-updated after SMS callback")

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Auto-update MY SMS Setting Failed")

    # Update Bulk SMS Result row (if exists)
    try:
        brec = frappe.db.exists("Bulk SMS Result", {"central_log_id": log_id})
        if brec:
            frappe.db.set_value("Bulk SMS Result", brec, "status", status)
            # Optionally store any gateway response in error_message if failed
            if status == "Failed":
                # If central provided a message, use it; otherwise leave blank
                frappe.db.set_value("Bulk SMS Result", brec, "error_message", None)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Failed updating Bulk SMS Result")

    # Realtime notify logged-in users about failure (so they get popup)
    if status == "Failed":
        try:
            frappe.publish_realtime(
                event="sms_status_update",
                message={"phone": phone, "status": status, "log_id": log_id},
                user=None,
            )
        except Exception:
            pass

    return {"status": "ok"}


CENTRAL_SEND_METHOD = "haron_sms_gateway.api.send_sms_from_central"


def enqueue_bulk_sms(doc, method):
    """Enqueue the background worker that processes the Bulk SMS"""
    # doc is the Bulk SMS document
    enqueue(
        "customer_sms.api.process_bulk_sms",
        bulk_name=doc.name,
        enqueue_after_commit=True,
    )


CENTRAL_SEND_METHOD = "haron_sms_gateway.api.send_sms_from_central"


@frappe.whitelist()
def process_bulk_sms(bulk_name):
    """
    Background job:
     - parse bulk.recipients (multiline)
     - call central send API for each phone
     - populate Bulk SMS Result rows
     - create Client SMS Log entries (Queued) for each recipient
     - maintain accurate sent/failed counters
    """
    bulk = frappe.get_doc("Bulk SMS", bulk_name)
    bulk.status = "Processing"
    frappe.db.set_value("Bulk SMS", bulk.name, "status", "Processing")

    settings = frappe.get_single("MY SMS Setting")
    central_base = (settings.central_api_url or "").rstrip("/")
    api_key = settings.api_key
    sender_name = settings.sender_name
    callback_url = (
        f"{frappe.utils.get_url()}/api/method/customer_sms.api.update_sms_status"
    )

    # parse recipients (split by newline, comma, semicolon)
    raw = bulk.recipients or ""
    phones = [p.strip() for p in re.split(r"[\n,;]+", raw) if p.strip()]

    total = len(phones)
    frappe.db.set_value("Bulk SMS", bulk.name, "created_count", total)

    sent_count = 0
    failed_count = 0

    for idx, phone in enumerate(phones):
        row_name = None
        try:
            # Add a result row (Pending)
            bulk.append("results", {"phone": phone, "status": "Pending"})
            bulk.save(ignore_permissions=True)
            frappe.db.commit()

            last_child = bulk.get("results")[-1]
            row_name = last_child.name
        except Exception:
            frappe.log_error(frappe.get_traceback(), "Failed to append Bulk SMS Result")

        try:
            payload = {
                "phone": phone,
                "message": bulk.message,
                "api_key": api_key,
                "customer_site": frappe.local.site,
                "callback_url": callback_url,
                "sender_name": sender_name,
            }

            send_url = f"{central_base}/api/method/{CENTRAL_SEND_METHOD}"
            resp = requests.post(send_url, json=payload, timeout=15)

            # Handle non-JSON or failed response
            try:
                resp_json = resp.json()
            except Exception:
                failed_count += 1
                if row_name:
                    frappe.db.set_value("Bulk SMS Result", row_name, "status", "Failed")
                    frappe.db.set_value(
                        "Bulk SMS Result",
                        row_name,
                        "error_message",
                        f"Central non-JSON response: {resp.text[:300]}",
                    )
                frappe.db.commit()
                continue

            data = resp_json.get("message", resp_json)

            # Central response handling
            if isinstance(data, dict) and data.get("status") == "queued":
                central_log_id = data.get("log_id")
                sent_count += 1

                if row_name:
                    frappe.db.set_value("Bulk SMS Result", row_name, "status", "Queued")
                    frappe.db.set_value(
                        "Bulk SMS Result", row_name, "central_log_id", central_log_id
                    )

                # Create Client SMS Log
                if not frappe.db.exists("Client SMS Log", {"log_id": central_log_id}):
                    frappe.get_doc(
                        {
                            "doctype": "Client SMS Log",
                            "log_id": central_log_id,
                            "phone": phone,
                            "sender_name": sender_name,
                            "message": bulk.message,
                            "status": "Queued",
                            "customer_site": frappe.local.site,
                        }
                    ).insert(ignore_permissions=True)

            else:
                failed_count += 1
                err_msg = data.get("message") if isinstance(data, dict) else str(data)
                if row_name:
                    frappe.db.set_value("Bulk SMS Result", row_name, "status", "Failed")
                    frappe.db.set_value(
                        "Bulk SMS Result", row_name, "error_message", err_msg
                    )

            # Progress commit occasionally
            if idx % 10 == 0:
                frappe.db.commit()

        except Exception:
            failed_count += 1
            frappe.log_error(
                frappe.get_traceback(), f"process_bulk_sms failed for {phone}"
            )
            if row_name:
                frappe.db.set_value("Bulk SMS Result", row_name, "status", "Failed")
                frappe.db.set_value(
                    "Bulk SMS Result",
                    row_name,
                    "error_message",
                    "Internal error - check logs",
                )
            frappe.db.commit()

    # Finalize totals and status
    frappe.db.set_value("Bulk SMS", bulk.name, "sent_count", sent_count)
    frappe.db.set_value("Bulk SMS", bulk.name, "failed_count", failed_count)
    frappe.db.set_value("Bulk SMS", bulk.name, "status", "Completed")

    frappe.db.commit()
    frappe.logger().info(
        f"Bulk SMS '{bulk.name}' completed: Sent={sent_count}, Failed={failed_count}"
    )
