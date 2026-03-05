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

if __name__ == '__main__':
    unittest.main()
