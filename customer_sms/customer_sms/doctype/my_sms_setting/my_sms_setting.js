frappe.ui.form.on("MY SMS Setting", {
	before_save(frm) {
		// Automatically detect site name only if not already set
		if (!frm.doc.customer_site) {
			// Get the actual ERPNext site name (works even in multi-tenant setup)
			const site_name = frappe.boot.sitename || window.location.hostname;
			frm.set_value("customer_site", site_name);
		}
	},
	refresh(frm) {
		if ((frm.doc.test_sms_count || 0) < 3) {
			frm.add_custom_button("Test SMS", () => {
				send_test_sms(frm);
			});
		} else {
			frm.remove_custom_button("Test SMS");
			// frappe.msgprint("You have reached the 3 test SMS limit.");
		}

		if (!frm.doc.api_key || !frm.doc.central_api_url || !frm.doc.sender_name) {
			frappe.msgprint("Please fill Central API URL, API Key, and Sender Name first.");
			return;
		}

		frm.add_custom_button(__("Sync from Central Server"), function () {
			if (!frm.doc.api_key || !frm.doc.central_api_url) {
				frappe.msgprint(__("Missing API key or Central Server URL."));
				return;
			}

			frappe.call({
				method: "customer_sms.api.request_sms_update",
				args: {
					api_key: frm.doc.api_key,
					central_server_url: frm.doc.central_api_url,
				},
				freeze: true,
				freeze_message: __("Fetching latest SMS info from central server..."),
				callback: function (r) {
					console.log("Response from central server:", r);

					try {
						// Handle success
						if (
							r.message?.status === "success" ||
							r.message?.message?.status === "success"
						) {
							frappe.msgprint(
								__("Latest SMS Gateway settings fetched successfully.")
							);
							return;
						}

						// Handle known error from Python
						if (r.message?.status === "error" || r.message?.msg) {
							frappe.msgprint(__("Failed to fetch SMS info: ") + r.message.msg);
							return;
						}

						// Handle unexpected response
						frappe.msgprint(__("Failed to fetch SMS info: Unknown response format."));
					} catch (e) {
						// Handle network or internal JS errors
						console.error("Error handling response:", e);
						frappe.msgprint(__("Network error: Unable to contact central server."));
					}
				},
			});
		});

		// if (!frm.doc.api_key) return;

		// frappe.call({
		// 	method: "customer_sms.api.request_sms_update",
		// 	args: {
		// 		api_key: frm.doc.api_key,
		// 		central_server_url: frm.doc.central_api_url,
		// 	},
		// 	freeze: true,
		// 	freeze_message: __("Fetching latest SMS info from central server..."),
		// 	callback: function (r) {
		// 		console.log("hellow world");
		// 		console.log(r);
		// 		if (r.message && r.message.status === "success") {
		// 			frappe.msgprint(__("Latest SMS Gateway settings fetched successfully."));
		// 		} else {
		// 			frappe.msgprint(
		// 				__("Failed to fetch SMS info: ") + (r.message?.msg || "Unknown error")
		// 			);
		// 		}
		// 	},
		// });

		// const apiUrl = `${frm.doc.central_api_url}/api/method/haron_sms_gateway.api.get_api_key_info`;

		// // Show loading message
		// frappe.dom.freeze("Fetching API Key Info...");

		// fetch(apiUrl + `?api_key=${frm.doc.api_key}&customer_site=${frm.doc.customer_site}`)
		// 	.then((res) => {
		// 		if (!res.ok) throw new Error("Failed to connect to Central API");
		// 		return res.json();
		// 	})
		// 	.then((data) => {
		// 		frappe.dom.unfreeze();

		// 		if (data.message) {
		// 			const info = data.message;

		// 			// Populate the fields (you can add these as read-only fields)
		// 			frm.set_value("valid_from", info.valid_from);
		// 			frm.set_value("valid_upto", info.valid_upto);
		// 			frm.set_value("status", info.status);
		// 			frm.set_value("daily_limit", String(info.daily_limit));
		// 			frm.set_value("sms_sent_today", String(info.sms_sent_today));
		// 			frm.set_value("remaining", String(info.remaining));
		// 			frm.save();

		// 			// frappe.msgprint({
		// 			// 	title: "API Info Updated",
		// 			// 	message: `
		// 			//         <b>Valid From:</b> ${info.valid_from}<br>
		// 			//         <b>Valid Upto:</b> ${info.valid_upto}<br>
		// 			//         <b>Daily Limit:</b> ${info.daily_limit}<br>
		// 			//         <b>SMS Sent Today:</b> ${info.sms_sent_today}<br>
		// 			//         <b>Remaining:</b> ${info.remaining}
		// 			//     `,
		// 			// 	indicator: "green",
		// 			// });

		// 			frm.refresh_fields();
		// 		} else {
		// 			frappe.msgprint("No info returned from Central Server.");
		// 		}
		// 	})
		// 	.catch((err) => {
		// 		frappe.dom.unfreeze();
		// 		frappe.msgprint({
		// 			title: "Error Fetching API Info",
		// 			message: err.message,
		// 			indicator: "red",
		// 		});
		// 	});
	},
});

function send_test_sms(frm) {
	const d = new frappe.ui.Dialog({
		title: "Send Test SMS",
		fields: [
			{ label: "Phone", fieldname: "phone", fieldtype: "Data", reqd: 1, default: "+2519" },
			{
				label: "Message",
				fieldname: "message",
				fieldtype: "Small Text",
				reqd: 1,
				default: "This is a test message.",
				read_only: 1,
			},
		],
		primary_action_label: "Send",
		primary_action(values) {
			const apiUrl = `${frm.doc.central_api_url}/api/method/haron_sms_gateway.api.send_sms_from_central`;

			frappe.dom.freeze("Sending test SMS...");

			const payload = {
				phone: values.phone,
				message: values.message,
				api_key: frm.doc.api_key,
				customer_site: frm.doc.customer_site,
				sender_name: frm.doc.sender_name || "",
				is_test: true, // mark this as test SMS
			};

			fetch(apiUrl, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(payload),
			})
				.then(async (res) => {
					frappe.dom.unfreeze();

					let rawText = await res.text();
					let data = null;
					try {
						data = JSON.parse(rawText);
					} catch {
						data = null; // not valid JSON
					}

					// let responseMsg =
					// 	data && data.message
					// 		? typeof data.message === "string"
					// 			? data.message
					// 			: JSON.stringify(data.message)
					// 		: rawText || "No response from server.";

					let responseMsg = "";
					if (data) {
						// if frappe API returned {message: {...}} or {status, message}
						if (typeof data.message === "string") {
							responseMsg = data.message;
						} else if (data.message && typeof data.message === "object") {
							// nested structure (ex: {"status":"error","message":"Invalid"})
							responseMsg =
								data.message.message ||
								data.message.status ||
								JSON.stringify(data.message);
						} else if (data.status && data.message) {
							responseMsg = data.message;
						} else {
							responseMsg = JSON.stringify(data);
						}
					} else {
						responseMsg = rawText || "No response from server.";
					}

					frappe.msgprint({
						title: res.ok ? "✅ SMS Response" : "❌ Failed to Send SMS",
						message: `<pre style="white-space: pre-wrap;">${responseMsg}</pre>`,
						indicator: res.ok ? "green" : "red",
					});

					// ✅ Only count if SMS is successfully queued
					if (res.ok && data?.message?.status === "queued") {
						let newCount = (frm.doc.test_sms_count || 0) + 1;
						frappe.db
							.set_value("MY SMS Setting", frm.doc.name, {
								test_sms_count: newCount,
							})
							.then(() => {
								frappe.show_alert({
									message: `Test SMS sent successfully (${newCount}/3)`,
									indicator: "green",
								});
								frm.reload_doc();
							});
					}

					d.hide();
				})
				.catch((err) => {
					frappe.dom.unfreeze();
					frappe.msgprint({
						title: "Network Error",
						message: err.message,
						indicator: "red",
					});
				});
		},
	});
	d.show();
}

// frappe.ui.form.on("MY SMS Setting", {
// 	refresh(frm) {
// 		if (!frm.is_new()) {
// 			frm.add_custom_button("🔄 Sync API Info", () => {
// 				sync_api_info(frm);
// 			});
// 		}
// 	},

// 	before_save(frm) {
// 		if (!frm.doc.customer_site) {
// 			const site_name = frappe.boot.sitename || window.location.hostname;
// 			frm.set_value("customer_site", site_name);
// 		}
// 	},
// });

// function sync_api_info(frm) {
// 	if (!frm.doc.api_key || !frm.doc.central_api_url || !frm.doc.sender_name) {
// 		frappe.msgprint("Please fill Central API URL, API Key, and Sender Name first.");
// 		return;
// 	}

// 	const apiUrl = `${frm.doc.central_api_url}/api/method/haron_sms_gateway.api.get_api_key_info`;
// 	const fullUrl = `${apiUrl}?api_key=${frm.doc.api_key}&customer_site=${frm.doc.customer_site}`;

// 	frappe.dom.freeze("Fetching API Key Info...");

// 	fetch(fullUrl)
// 		.then((res) => {
// 			if (!res.ok) throw new Error("Failed to connect to Central API");
// 			return res.json();
// 		})
// 		.then((data) => {
// 			frappe.dom.unfreeze();

// 			if (!data.message) {
// 				frappe.msgprint("No info returned from Central Server.");
// 				return;
// 			}

// 			const info = data.message;
// 			let updated = false;

// 			const fields = [
// 				"valid_from",
// 				"valid_upto",
// 				"status",
// 				"daily_limit",
// 				"sms_sent_today",
// 				"remaining",
// 			];

// 			fields.forEach((f) => {
// 				if (frm.doc[f] !== String(info[f])) {
// 					frm.set_value(f, String(info[f]));
// 					updated = true;
// 				}
// 			});

// 			if (updated) {
// 				frm.save();
// 				show_sync_dialog(info);
// 			} else {
// 				frappe.msgprint({
// 					title: "No Updates Found",
// 					message: "Your API info is already up to date.",
// 					indicator: "blue",
// 				});
// 			}
// 		})
// 		.catch((err) => {
// 			frappe.dom.unfreeze();
// 			frappe.msgprint({
// 				title: "Error Fetching API Info",
// 				message: err.message,
// 				indicator: "red",
// 			});
// 		});
// }

// function show_sync_dialog(info) {
// 	const dialog = new frappe.ui.Dialog({
// 		title: "✅ API Info Synced",
// 		size: "small",
// 		primary_action_label: "Close",
// 		primary_action() {
// 			dialog.hide();
// 		},
// 	});

// 	const html = `
// 		<div style="padding-top:10px;">
// 			<table class="table table-bordered">
// 				<tr><td><b>Valid From</b></td><td>${info.valid_from || "—"}</td></tr>
// 				<tr><td><b>Valid Upto</b></td><td>${info.valid_upto || "—"}</td></tr>
// 				<tr><td><b>Status</b></td><td>${info.status || "—"}</td></tr>
// 				<tr><td><b>Daily Limit</b></td><td>${info.daily_limit || "—"}</td></tr>
// 				<tr><td><b>SMS Sent Today</b></td><td>${info.sms_sent_today || "—"}</td></tr>
// 				<tr><td><b>Remaining</b></td><td>${info.remaining || "—"}</td></tr>
// 			</table>
// 		</div>
// 	`;

// 	dialog.$body.html(html);
// 	dialog.show();
// }

// frappe.ui.form.on("MY SMS Setting", {
// 	refresh(frm) {
// 		frm.add_custom_button("Test SMS", () => {
// 			if (!frm.doc.central_api_url || !frm.doc.api_key || !frm.doc.customer_site) {
// 				frappe.msgprint(
// 					"⚠️ Please configure Central API URL, API Key, and Customer Site first."
// 				);
// 				return;
// 			}

// 			const d = new frappe.ui.Dialog({
// 				title: "Send Test SMS",
// 				fields: [
// 					{
// 						label: "Phone Number",
// 						fieldname: "phone",
// 						fieldtype: "Data",
// 						reqd: true,
// 						placeholder: "+2519XXXXXXXX",
// 					},
// 					{
// 						label: "Message",
// 						fieldname: "message",
// 						fieldtype: "Small Text",
// 						reqd: true,
// 						placeholder: "Enter your test message",
// 					},
// 				],
// 				primary_action_label: "Send SMS",
// 				primary_action(values) {
// 					const apiUrl = `${frm.doc.central_api_url}/api/method/haron_forex.api.send_sms_from_central`;

// 					frappe.dom.freeze("Sending test SMS...");

// 					const payload = {
// 						phone: values.phone,
// 						message: values.message,
// 						api_key: frm.doc.api_key,
// 						customer_site: frm.doc.customer_site,
// 						sender_name: frm.doc.sender_name || "",
// 					};

// 					fetch(apiUrl, {
// 						method: "POST",
// 						headers: {
// 							"Content-Type": "application/json",
// 						},
// 						body: JSON.stringify(payload),
// 					})
// 						.then(async (res) => {
// 							frappe.dom.unfreeze();
// 							let data;
// 							let rawText = await res.text();

// 							try {
// 								data = JSON.parse(rawText);
// 							} catch {
// 								// response was not valid JSON
// 								data = null;
// 							}

// 							let responseMsg = "";

// 							if (data && data.message) {
// 								if (typeof data.message === "string") {
// 									responseMsg = data.message;
// 								} else if (typeof data.message === "object") {
// 									responseMsg =
// 										`<b>Status:</b> ${data.message.status || "Unknown"}<br>` +
// 										`<b>Details:</b> ${JSON.stringify(
// 											data.message.details || {},
// 											null,
// 											2
// 										)}`;
// 								} else {
// 									responseMsg = JSON.stringify(data.message);
// 								}
// 							} else {
// 								// fallback to raw text if unknown
// 								responseMsg = rawText || "No response from server.";
// 							}

// 							frappe.msgprint({
// 								title: res.ok ? "✅ SMS Response" : "❌ Failed to Send SMS",
// 								message: `<pre style="white-space: pre-wrap;">${responseMsg}</pre>`,
// 								indicator: res.ok ? "green" : "red",
// 							});

// 							d.hide();
// 						})
// 						.catch((err) => {
// 							frappe.dom.unfreeze();
// 							frappe.msgprint({
// 								title: "Network Error",
// 								message: err.message,
// 								indicator: "red",
// 							});
// 						});
// 				},
// 			});

// 			d.show();
// 		});
// 	},
// });
