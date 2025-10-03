frappe.ui.form.on("Client SMS Log", {
	refresh: function (frm) {
		if (frm.doc.status === "Failed") {
			frm.add_custom_button(
				__("Resend SMS"),
				function () {
					frappe.call({
						method: "customer_sms.api.resend_sms",
						args: {
							log_id: frm.doc.name,
						},
						callback: function (r) {
							if (!r.exc) {
								frappe.msgprint(r.message.msg || "SMS Resend Request Sent");
								frm.reload_doc();
							}
						},
					});
				}
				// __("Actions")
			);
		}
	},
});

// frappe.ui.form.on("Client SMS Log", {
// 	refresh: function (frm) {
// 		if (frm.doc.status === "Failed") {
// 			frm.add_custom_button(__("Resend"), function () {
// 				frappe.call({
// 					method: "haron_forex.api.resend_sms", //http://127.0.0.1:8005/api/method/haron_forex.api.send_sms_from_central
// 					args: {
// 						log_name: frm.doc.name,
// 					},
// 					callback: function (r) {
// 						if (!r.exc) {
// 							frappe.msgprint(__("SMS Resent and queued again."));
// 							frm.reload_doc();
// 						}
// 					},
// 				});
// 			}).addClass("btn-primary");
// 		}
// 	},
// });
