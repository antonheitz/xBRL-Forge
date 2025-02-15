import uvicorn
import os
import logging
from .webapi import app

logger = logging.getLogger(__name__)
port = int(os.environ.get("XBRL_FORGE_PORT", "8000"))
uvicorn.run(app, host="0.0.0.0", port=port)