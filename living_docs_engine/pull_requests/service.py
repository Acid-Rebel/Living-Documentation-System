from typing import Dict, List, Optional
from datetime import datetime
from .models import DocumentationPR, PRStatus, Review, ReviewStatus

class PRService:
    """Service to handle the logic of Documentation Pull Requests."""
    
    def __init__(self):
        # In-memory storage for the scope of this implementation iteration. 
        # In a real scenario, this would interact with a database.
        self._prs: Dict[str, DocumentationPR] = {}
        
    def create_pr(self, title: str, description: str, commit_hash: str, doc_content: str, author_id: str) -> DocumentationPR:
        pr = DocumentationPR(
            title=title,
            description=description,
            commit_hash=commit_hash,
            doc_content=doc_content,
            author_id=author_id
        )
        self._prs[pr.pr_id] = pr
        return pr

    def get_pr(self, pr_id: str) -> Optional[DocumentationPR]:
        return self._prs.get(pr_id)

    def list_prs(self) -> List[DocumentationPR]:
        return list(self._prs.values())
