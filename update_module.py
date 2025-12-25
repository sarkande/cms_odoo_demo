#!/usr/bin/env python3
import xmlrpc.client

# Connection parameters
url = "http://localhost:8219"
db = "odoo"
username = "admin"
password = "admin"

# Authenticate
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

if uid:
    print(f"Authenticated as user {uid}")

    # Get models proxy
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    # Search for the module
    module_ids = models.execute_kw(db, uid, password,
        'ir.module.module', 'search',
        [[['name', '=', 'cms_sarkande']]])

    if module_ids:
        print(f"Found module cms_sarkande with ID {module_ids[0]}")

        # Upgrade the module
        result = models.execute_kw(db, uid, password,
            'ir.module.module', 'button_immediate_upgrade',
            [module_ids])

        print("Module updated successfully!")
        print(f"Result: {result}")
    else:
        print("Module cms_sarkande not found")
else:
    print("Authentication failed")
