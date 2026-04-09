from app.database import SessionLocal
from app.models import Url
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime,timedelta, timezone
from sqlalchemy.orm import Session


def cleanUpExpiredLinks(db: Session) -> int:
    """Delete expired links. Returns number of deleted links."""
    try:
        # Use naive datetime (matches your database)
        now = datetime.utcnow()
        
        deleted_count = db.query(Url).filter(
            Url.expires_at < now
        ).delete()
        db.commit()
        print(f"🧹 Cleanup: deleted {deleted_count} expired links")
        return deleted_count
    except Exception as e:
        print(f"❌ Cleanup error: {e}")
        db.rollback()
        return 0



      


