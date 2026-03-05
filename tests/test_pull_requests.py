import unittest
from living_docs_engine.pull_requests import PRService, PRStatus, ReviewStatus

class TestPullRequestsModule(unittest.TestCase):
    def setUp(self):
        self.service = PRService()
        self.author_id = "user-123"
        self.title = "Update logic section"
        self.description = "Refactored core engine loop"
        self.commit_hash = "abc123def"
        self.doc_content = "New markdown documentation for the core logic."
        
    def test_create_pr(self):
        pr = self.service.create_pr(
            title=self.title,
            description=self.description,
            commit_hash=self.commit_hash,
            doc_content=self.doc_content,
            author_id=self.author_id
        )
        
        self.assertIsNotNone(pr.pr_id)
        self.assertEqual(pr.title, self.title)
        self.assertEqual(pr.status, PRStatus.OPEN)
        self.assertEqual(pr.author_id, self.author_id)
        
        # Ensure it's stored and retrievable
        retrieved_pr = self.service.get_pr(pr.pr_id)
        self.assertEqual(retrieved_pr.pr_id, pr.pr_id)
        
    def test_add_review_approve(self):
        pr = self.service.create_pr(
            title=self.title,
            description=self.description,
            commit_hash=self.commit_hash,
            doc_content=self.doc_content,
            author_id=self.author_id
        )
        
        reviewer_id = "user-456"
        self.service.add_review(pr.pr_id, reviewer_id, ReviewStatus.APPROVED, "Looks good!")
        
        updated_pr = self.service.get_pr(pr.pr_id)
        self.assertEqual(updated_pr.status, PRStatus.APPROVED)
        self.assertEqual(len(updated_pr.reviews), 1)
        self.assertEqual(updated_pr.reviews[0].reviewer_id, reviewer_id)
        
    def test_same_user_can_create_and_merge(self):
        # As per the prompt: "the same user can create the pull request and the same person can merge it"
        pr = self.service.create_pr(
            title=self.title,
            description=self.description,
            commit_hash=self.commit_hash,
            doc_content=self.doc_content,
            author_id=self.author_id
        )
        
        merged_pr = self.service.merge_pr(pr.pr_id, merged_by=self.author_id)
        
        self.assertEqual(merged_pr.status, PRStatus.MERGED)
        self.assertEqual(merged_pr.merged_by, self.author_id)
        self.assertIsNotNone(merged_pr.merged_at)
        
    def test_cannot_review_merged_pr(self):
        pr = self.service.create_pr(
            title=self.title,
            description=self.description,
            commit_hash=self.commit_hash,
            doc_content=self.doc_content,
            author_id=self.author_id
        )
        
        self.service.merge_pr(pr.pr_id, merged_by=self.author_id)
        
        with self.assertRaises(ValueError):
            self.service.add_review(pr.pr_id, "user-456", ReviewStatus.APPROVED)

if __name__ == '__main__':
    unittest.main()
