import configparser
import logging
import os
from pathlib import Path
from typing import Union

_cwdir = Path(__file__).parent

# the environment variable for the site configuration file, highest priority.
ENV_CONFIG_PATH_NAME = "PYARCHAPPL_CONFIG_FILE"

_LOGGER = logging.getLogger(__name__)


def read_config(config_file: Union[Path, None] = None) -> dict:
    """ Read the configuration file as a dictionary.

    Parameters
    ----------
    config_file : Path or None
        The file path to the configuration file, if not set, use the default
        one distributed with the package.

    Returns
    -------
    r : dict
        A dictionary of the configurations.
    """
    if config_file is None:
        config_file = _cwdir.joinpath("default.ini")
    config = configparser.ConfigParser()
    _config_pth = config.read(config_file.expanduser())
    # utilized server config
    server_key = config['main']['use']
    if server_key not in config:
        raise RuntimeError(f"'{server_key}' section not found in {config_file}")
    server_config = dict(config[server_key])
    if 'url' not in server_config:
        raise RuntimeError(f"'url' not found in '{server_key}' section")
    # update admin_disabled with boolean data type
    if 'admin_disabled' in server_config:
        server_config['admin_disabled'] = config[server_key].getboolean('admin_disabled')
    all_config = {
        'server': server_config,
        'path': _config_pth[0]
    }
    # commands default options
    if 'cli.pyarchappl-get' in config:
        get_config = dict(config['cli.pyarchappl-get'])
        if 'use_json' in get_config:
            get_config['use_json'] = config['cli.pyarchappl-get'].getboolean('use_json')
        all_config['cli.pyarchappl-get'] = get_config

    # misc options
    if 'misc' in config:
        misc_config = dict(config['misc'])
        if 'local_timezone' in misc_config:
            misc_config['local_timezone'] = config['misc'].get('local_timezone')
        all_config['misc'] = misc_config

    return all_config


def get_config_path() -> Path:
    """ Return the configuration file path, searching priority:

    0. env: PYARCHAPPL_CONFIG_FILE
    1. ~/.pyarchappl/config.ini
    2. /etc/pyarchappl/config.ini
    3. <package-dir>/config/default.ini

    Returns
    -------
    pth : Path
        The path of the configuration file.
    """
    env_config_path = os.environ.get(ENV_CONFIG_PATH_NAME, None)
    if env_config_path is not None:
        return Path(env_config_path).expanduser()
    if Path("~/.pyarchappl/config.ini").expanduser().is_file():
        return Path("~/.pyarchappl/config.ini").expanduser()
    elif Path("/etc/pyarchappl/config.ini").is_file():
        return Path("/etc/pyarchappl/config.ini")
    else:
        return _cwdir.joinpath("default.ini")


config_path: Path = get_config_path()
_LOGGER.info(f"Using site config file: {config_path}")
SITE_CONFIG: dict = read_config(config_path)
SITE_SERVER_CONFIG: dict = SITE_CONFIG['server']
if 'admin_port' in SITE_SERVER_CONFIG:
    SITE_ADMIN_URL = f"{SITE_SERVER_CONFIG['url']}:{SITE_SERVER_CONFIG['admin_port']}"
else:
    SITE_ADMIN_URL = f"{SITE_SERVER_CONFIG['url']}"
_LOGGER.debug(f"Site configuration admin client: {SITE_ADMIN_URL}")

if 'data_port' in SITE_SERVER_CONFIG:
    SITE_DATA_URL = f"{SITE_SERVER_CONFIG['url']}:{SITE_SERVER_CONFIG['data_port']}"
else:
    SITE_DATA_URL = f"{SITE_SERVER_CONFIG['url']}"
_LOGGER.debug(f"Site configuration data client: {SITE_DATA_URL}")

SITE_DATA_FORMAT: str = SITE_SERVER_CONFIG.get('data_format', 'raw')
_LOGGER.debug(f"Site configuration data_format: {SITE_DATA_FORMAT}")