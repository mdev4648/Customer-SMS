import frappe
import requests


# def send_sms_on_submit(doc, method):
#     import json

#     phone = doc.phone
#     message = doc.message

#     if not phone or not message:
#         frappe.throw("Phone and message are required to send SMS.")

#     settings = frappe.get_single("Custom Sms Setting")
#     CENTRAL_SMS_API = settings.central_api_url
#     CENTRAL_API_KEY = settings.api_key

#     url = f"{CENTRAL_SMS_API}/api/method/haron_forex.api.send_sms_from_central"

#     payload = {
#         "phone": phone,
#         "message": message,
#         "api_key": CENTRAL_API_KEY,
#         "customer_site": frappe.local.site,
#         # call back url to from central to client
#         "callback_url": f"{frappe.utils.get_url()}/api/method/customer_sms.api.update_sms_status",
#     }
#     headers = {"Content-Type": "application/json"}

#     try:
#         res = requests.post(url, json=payload, headers=headers, timeout=10)

#         if res.status_code != 200:
#             # Parse clean frappe error
#             msg = res.text
#             try:
#                 error_json = res.json()
#                 if "_server_messages" in error_json:
#                     server_msgs = json.loads(error_json["_server_messages"])
#                     if server_msgs:
#                         inner_msg = json.loads(server_msgs[0])
#                         msg = inner_msg.get("message", msg)
#                 elif "exception" in error_json:
#                     msg = error_json.get("exception")
#             except Exception:
#                 pass

#             frappe.throw(msg)

#         #  unwrap frappe "message"
#         response_json = res.json()
#         data = response_json.get("message", response_json)

#         if data.get("status") == "queued":
#             frappe.msgprint(f"SMS queued for {phone}")
#         else:
#             frappe.throw(f"Unexpected Response: {data}")

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "SMS Sending Failed")
#         frappe.throw(str(e))


def send_sms_on_submit(doc, method):
    import requests
    import json

    phone = doc.phone
    message = doc.message

    if not phone or not message:
        frappe.throw("Phone and message are required to send SMS.")

    settings = frappe.get_single("Custom Sms Setting")
    CENTRAL_SMS_API = settings.central_api_url
    CENTRAL_API_KEY = settings.api_key

    url = f"{CENTRAL_SMS_API}/api/method/haron_forex.api.send_sms_from_central"

    payload = {
        "phone": phone,
        "message": message,
        "api_key": CENTRAL_API_KEY,
        "customer_site": frappe.local.site,
        "callback_url": f"{frappe.utils.get_url()}/api/method/customer_sms.api.update_sms_status",
    }

    headers = {"Content-Type": "application/json"}

    try:
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        res.raise_for_status()
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "SMS Sending Failed")
        frappe.throw(str(e))


# @frappe.whitelist()
# def resend_sms(log_id):
#     """Call Central Server's resend API to re-queue failed SMS from client"""
#     log = frappe.get_doc("Client SMS Log", log_id)

#     if log.status != "Failed":
#         frappe.throw("Only Failed SMS can be resent")

#     # Get settings (where you saved central API details)
#     settings = frappe.get_single("Custom Sms Setting")
#     CENTRAL_SERVER_URL = settings.central_api_url  # e.g. http://sms.com:8005
#     CENTRAL_API_KEY = settings.api_key

#     # Construct the URL of central resend API
#     central_resend_url = f"{CENTRAL_SERVER_URL}/api/method/haron_forex.api.resend_sms"

#     try:
#         res = requests.post(
#             central_resend_url,
#             data={
#                 "log_name": log.log_id,  # Important: store central log id on client log
#                 "api_key": CENTRAL_API_KEY,
#                 "customer_site": frappe.local.site,
#             },
#             timeout=10,
#         )

#         # Try to parse JSON safely
#         try:
#             response_json = res.json()
#         except Exception:
#             return {
#                 "status": "error",
#                 "msg": res.text[:300] or "Central server returned non-JSON",
#             }

#         if response_json.get("status") == "queued":
#             # Update client log to Queued again
#             log.status = "Queued"
#             log.save(ignore_permissions=True)
#             frappe.db.commit()

#             return {"status": "success", "msg": "SMS re-queued successfully"}
#         else:
#             return {"status": "error", "msg": response_json}

#     except Exception as e:
#         return {"status": "error", "msg": str(e)}


import json


@frappe.whitelist()
def resend_sms(log_id):
    """Call Central Server's resend API to re-queue failed SMS from client"""
    log = frappe.get_doc("Client SMS Log", log_id)

    if log.status != "Failed":
        frappe.throw("Only Failed SMS can be resent")

    # Get settings
    settings = frappe.get_single("Custom Sms Setting")
    CENTRAL_SERVER_URL = settings.central_api_url
    CENTRAL_API_KEY = settings.api_key

    central_resend_url = f"{CENTRAL_SERVER_URL}/api/method/haron_forex.api.resend_sms"

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
def update_sms_status(log_id, status, phone=None, message=None, customer_site=None):
    """
    Central server will call this after sending SMS.
    Updates or creates Client SMS Log status.
    """

    existing_log = frappe.db.exists("Client SMS Log", {"log_id": log_id})

    if existing_log:
        frappe.db.set_value("Client SMS Log", existing_log, "status", status)
    else:
        if not phone or not message:
            return {
                "status": "error",
                "msg": "Phone and message required to create new Client SMS Log",
            }

        log_doc = frappe.get_doc(
            {
                "doctype": "Client SMS Log",
                "log_id": log_id,
                "phone": phone,
                "message": message,
                "status": status,
                "customer_site": customer_site or frappe.local.site,
            }
        )
        log_doc.insert(ignore_permissions=True)

    frappe.db.commit()

    if status == "Failed":
        frappe.publish_realtime(
            event="sms_status_update",
            message={"phone": phone, "status": status, "log_id": log_id},
            user=None,
        )
        frappe.logger().info(f"Realtime SMS Failed event sent for {phone}")

    return {"status": "ok", "msg": f"Log {status.lower()}"}
