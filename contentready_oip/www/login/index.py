import frappe
from frappe.utils.password import get_decrypted_password
from frappe.utils.oauth import get_oauth2_authorize_url, get_oauth_keys
from frappe.utils.html_utils import get_icon_html


def get_context(context):
    context["provider_logins"] = []
    redirect_to = "/dashboard"
    # redirect_to = frappe.local.request.args.get("redirect-to")
    providers = [
        i.name
        for i in frappe.get_all("Social Login Key", filters={"enable_social_login": 1})
    ]

    for provider in providers:
        client_id, base_url = frappe.get_value(
            "Social Login Key", provider, ["client_id", "base_url"]
        )
        client_secret = get_decrypted_password(
            "Social Login Key", provider, "client_secret"
        )
        icon = get_icon_html(
            frappe.get_value("Social Login Key", provider, "icon"), small=False
        )
        if get_oauth_keys(provider) and client_secret and client_id and base_url:
            context.provider_logins.append(
                {
                    "name": provider,
                    "provider_name": frappe.get_value(
                        "Social Login Key", provider, "provider_name"
                    ),
                    "auth_url": get_oauth2_authorize_url(provider, redirect_to),
                    "icon": icon,
                }
            )
            context["social_login"] = True
