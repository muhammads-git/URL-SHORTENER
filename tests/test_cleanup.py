from datetime import datetime, timedelta
import time
from app.database import SessionLocal
from app.models import Url
from app.services.cleanup_service import cleanUpExpiredLinks

def test_cleanup_deletes_expired_link():
    db = SessionLocal()
    
    # Generate UNIQUE short code using timestamp
    unique_code = f"test_expired_{int(time.time())}"
    
    # Create expired link (using naive datetime - no timezone)
    expired_link = Url(
        shortUrl=unique_code,  # ← Unique every time!
        longUrl="https://google.com",
        clicks=0,
        expires_at=datetime.utcnow() - timedelta(days=1)
    )
    db.add(expired_link)
    db.commit()
    
    link_id = expired_link.id
    
    # Run cleanup
    deleted = cleanUpExpiredLinks(db)
    
    # Check
    assert isinstance(deleted, int)
    assert deleted >= 1
    
    # Verify link is gone
    found = db.query(Url).filter(Url.id == link_id).first()
    assert found is None
    
    db.close()


def test_cleanup_keeps_valid_link():
    db = SessionLocal()
    
    # Generate UNIQUE short code
    unique_code = f"test_valid_{int(time.time())}"
    
    # Create valid link
    valid_link = Url(
        shortUrl=unique_code,  # ← Unique every time!
        longUrl="https://google.com",
        clicks=0,
        expires_at=datetime.utcnow() + timedelta(days=1)
    )
    db.add(valid_link)
    db.commit()
    
    link_id = valid_link.id
    
    # Run cleanup
    deleted = cleanUpExpiredLinks(db)
    
    # Should return 0 (nothing deleted)
    assert deleted == 0
    
    # Verify link still exists
    found = db.query(Url).filter(Url.id == link_id).first()
    assert found is not None
    
    # Clean up test data
    db.delete(found)
    db.commit()
    db.close()