import uuid
from enum import Enum
from typing import List, Optional
from dataclasses import dataclass, field
from datetime import datetime

class PRStatus(Enum):
    OPEN = "OPEN"
    APPROVED = "APPROVED"
    MERGED = "MERGED"
    REJECTED = "REJECTED"
    CLOSED = "CLOSED"

class ReviewStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"

@dataclass
class Review:
    reviewer_id: str
    status: ReviewStatus = ReviewStatus.PENDING
    comment: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
