frappe.ui.form.on("MY SMS Setting", {
	refresh: function (frm) {
		if (!frm.doc.api_key) return;

		frappe.call({
			method: "customer_sms.api.request_sms_update",
			args: {
				api_key: frm.doc.api_key,
				central_server_url: frm.doc.central_server_url,
			},
			freeze: true,
			freeze_message: __("Fetching latest SMS info from central server..."),
			callback: function (r) {
				if (r.message && r.message.status === "success") {
					frappe.msgprint(__("Latest SMS Gateway settings fetched successfully."));
				} else {
					frappe.msgprint(
						__("Failed to fetch SMS info: ") + (r.message?.msg || "Unknown error")
					);
				}
			},
		});
	},
});
