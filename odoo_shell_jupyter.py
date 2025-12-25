import odoo
import odoo.tools.config
from odoo import api, SUPERUSER_ID
from odoo.service import db as service_db

def get_env(db_name=None):
    """Retourne un env Odoo pour la base choisie, ou auto-détecte si une seule DB existe."""
    # Config identique au docker-compose
    odoo.tools.config['db_host'] = 'db'
    odoo.tools.config['db_user'] = 'odoo'
    odoo.tools.config['db_password'] = 'odoo'

    # Si aucune DB spécifiée, essayer de la trouver
    if not db_name:
        dbs = service_db.list_dbs(True)  # True => inclut bases filtrées par dbfilter
        if not dbs:
            raise Exception("❌ Aucune base trouvée")
        if len(dbs) > 1:
            raise Exception(f"⚠️ Plusieurs bases trouvées : {dbs}. Spécifie db_name.")
        db_name = dbs[0]

    # Initialiser le registre
    odoo.sql_db.close_all()
    odoo.modules.registry.Registry.new(db_name)

    registry = odoo.registry(db_name)
    cr = registry.cursor()
    env = api.Environment(cr, SUPERUSER_ID, {})
    print(f"✅ Contexte Odoo chargé pour '{db_name}' (env, cr disponibles)")
    return env, cr

