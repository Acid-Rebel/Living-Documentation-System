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

@dataclass
class DocumentationPR:
    title: str
    description: str
    commit_hash: str
    doc_content: str
    author_id: str
    
    pr_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: PRStatus = PRStatus.OPEN
    reviews: List[Review] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    merged_at: Optional[datetime] = None
    merged_by: Optional[str] = None
