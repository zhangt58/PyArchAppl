import os
from pathlib import Path
from archappl.config import read_config
from archappl.config import get_config_path
from archappl.config import ENV_CONFIG_PATH_NAME


def test_config_full(config_dir: Path):
    config_file = config_dir.joinpath("full.ini")
    conf = read_config(config_file)
    assert conf['path'] == config_file.resolve().as_posix()
    conf['server'].pop('admin_disabled')
    assert conf['server'] == {
        'url': 'http://127.0.0.1',
        'admin_port': '17665',
        'data_port': '17668',
        'data_format': 'raw'
    }
    assert conf['cli.pyarchappl-get'] == {
        'use_json': False
    }


def test_config_pkg_default(config_dir: Path):
    conf = read_config()
    conf_filename = Path(conf.pop('path')).name
    pkg_config_file = config_dir.parent.parent.joinpath("config").joinpath("default.ini")
    conf_ = read_config(pkg_config_file)
    conf_filename_ = Path(conf_.pop('path')).name
    assert conf_filename == conf_filename_
    assert conf == conf_


def test_config_path_env(config_dir: Path):
    os.environ[ENV_CONFIG_PATH_NAME] = config_dir.joinpath("full.ini").as_posix()
    config_file = get_config_path()
    assert config_file == config_dir.joinpath("full.ini")
