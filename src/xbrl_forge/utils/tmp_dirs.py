import tempfile
import uuid
import os
import shutil
import logging

logger = logging.getLogger(__name__)

def create_tmp_dir() -> str:
    tmp_folder_path: str = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
    logger.info(f"Creating temporary directory at {tmp_folder_path}")
    os.mkdir(tmp_folder_path)
    return tmp_folder_path

def remove_tmp_dir(dir: str) -> None:
    shutil.rmtree(dir)
    logger.info(f"Removed temporary directory at {dir}")