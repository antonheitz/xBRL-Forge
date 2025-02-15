import logging
import os

def logger_conf(log_level: int = None):
    # if not provided directly
    if not log_level:
        # check env, defaut to info
        log_level = logging.getLevelNamesMapping().get(os.environ.get("XBRL_FORGE_LOGGING", "WARNING"))
    logging.basicConfig(level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger(__name__)
    logger.info(f"Configured Logger to level {logging.getLevelName(log_level)}")