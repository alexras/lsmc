import appdirs

_dirs = appdirs.AppDirs("LSMC", "alexras")

CONFIG_DIR = _dirs.user_config_dir
DATA_DIR = _dirs.user_data_dir
CACHE_DIR = _dirs.user_cache_dir
LOG_DIR = _dirs.user_log_dir
