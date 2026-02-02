from app.db.session import engine
from app.db.base import Base

from app.models.user import User  # noqa
from app.models.progress import StudentProgress  # noqa
from app.models.inventory import InventoryItem  # noqa

def init_db() -> None:
    Base.metadata.create_all(bind=engine)
