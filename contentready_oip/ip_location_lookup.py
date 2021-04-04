import os
import frappe
import IP2Location
from frappe.utils import get_site_path


def get_location(ip_addr):
    enable_geoip_lookup = frappe.get_value('OIP Configuration', '', 'enable_geoip_lookup')
    db_file = frappe.get_value('OIP Configuration', '', 'ip2location_database')[1:]
    if enable_geoip_lookup and db_file:
        db_path = os.path.abspath(os.path.join(get_site_path(), db_file))
        database = IP2Location.IP2Location(db_path)
        return database.get_all(ip_addr)
    else:
        return None

if __name__=="__main__":
    rec = get_location("8.8.8.8")
    print("Country Code:", rec.country_short)
    print("Country:", rec.country_long)
    print("Region:", rec.region)
    print("City:", rec.city)
    print("Lat:", rec.latitude)
    print("Long:", rec.longitude)			
    print("Zip:", rec.zipcode)
    print("Timezone:", rec.timezone)


