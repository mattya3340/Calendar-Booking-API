import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import logging
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.base_class import Base
from app.models import User, CalendarEvent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(db: Any) -> None:
    # Create all tables
    Base.metadata.create_all(bind=db.bind)
    
    user = db.query(User).filter(User.email == settings.FIRST_SUPERUSER).first()
    if not user:
        user_in = {
            "email": settings.FIRST_SUPERUSER,
            "hashed_password": get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            "full_name": "Initial Super User",
            "is_superuser": True,
            "is_active": True
        }
        db_obj = User(**user_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        logger.info("Initial superuser created")
    else:
        logger.info("Skipping superuser creation (already exists)")

def main() -> None:
    logger.info("Creating initial data")
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        init_db(db)
    finally:
        db.close()
    logger.info("Initial data created")

if __name__ == "__main__":
    main()
