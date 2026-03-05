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
        
    def add_review(self, pr_id: str, reviewer_id: str, status: ReviewStatus, comment: Optional[str] = None) -> Review:
        pr = self.get_pr(pr_id)
        if not pr:
            raise ValueError(f"PR with ID {pr_id} not found.")
            
        if pr.status in [PRStatus.MERGED, PRStatus.CLOSED]:
            raise ValueError("Cannot review a closed or merged PR.")
            
        review = Review(reviewer_id=reviewer_id, status=status, comment=comment)
        pr.reviews.append(review)
        
        # Update PR status based on reviews
        self._update_pr_status(pr)
        pr.updated_at = datetime.utcnow()
        return review
        
    def _update_pr_status(self, pr: DocumentationPR):
        """Helper to deduce PRStatus based on reviews."""
        if any(r.status == ReviewStatus.CHANGES_REQUESTED for r in pr.reviews):
            pr.status = PRStatus.REJECTED
        elif any(r.status == ReviewStatus.APPROVED for r in pr.reviews):
            pr.status = PRStatus.APPROVED
        else:
            pr.status = PRStatus.OPEN

    def merge_pr(self, pr_id: str, merged_by: str) -> DocumentationPR:
        pr = self.get_pr(pr_id)
        if not pr:
            raise ValueError(f"PR with ID {pr_id} not found.")
            
        if pr.status in [PRStatus.MERGED, PRStatus.CLOSED]:
            raise ValueError("PR is already merged or closed.")
            
        # For this iteration, same user can merge, but PR needs to be either directly merged or approved.
        # We will allow direct merges by the author for simplicity as per requirements ("the same user can create the pull request and the same person can merge it").
        
        pr.status = PRStatus.MERGED
        pr.merged_at = datetime.utcnow()
        pr.merged_by = merged_by
        pr.updated_at = datetime.utcnow()
        
        return pr
        
    def close_pr(self, pr_id: str) -> DocumentationPR:
        pr = self.get_pr(pr_id)
        if not pr:
            raise ValueError(f"PR with ID {pr_id} not found.")
            
        if pr.status in [PRStatus.MERGED, PRStatus.CLOSED]:
            raise ValueError("PR is already merged or closed.")
            
        pr.status = PRStatus.CLOSED
        pr.updated_at = datetime.utcnow()
        return pr
