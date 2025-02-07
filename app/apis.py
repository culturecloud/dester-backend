from typing import Dict
from app.settings import settings
from app.core.mongodb import MongoDB
from app.core.rclone import RCloneAPI


mongo = MongoDB(
    settings.MONGODB_URI,
    settings.MONGODB_DOMAIN,
    settings.MONGODB_USERNAME,
    settings.MONGODB_PASSWORD
)
rclone: Dict[int, RCloneAPI] = {}
