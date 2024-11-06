from archappl.config import SITE_SERVER_CONFIG
if not SITE_SERVER_CONFIG.get('admin_disabled', False):
    from archappl.admin import ArchiverMgmtClient
from archappl.data import ArchiverDataClient
