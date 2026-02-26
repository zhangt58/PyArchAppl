import logging
_LOGGER = logging.getLogger(__name__)

from archappl.config import SITE_SERVER_CONFIG
if not SITE_SERVER_CONFIG.get('admin_disabled', False):
    from archappl.admin import ArchiverMgmtClient
else:
    _LOGGER.warning(
        "ArchiverMgmtClient is not available as 'admin_disabled'")
from archappl.data import ArchiverDataClient
