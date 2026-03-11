#!/usr/bin/env python3
"""
Test script to reproduce and fix Google embedder 'list' object has no attribute 'embedding' error.
"""

import os
import sys
import logging
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Set up environment
from dotenv import load_dotenv
load_dotenv()

# Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

@pytest.mark.skipif(not os.getenv('GOOGLE_API_KEY'), reason="GOOGLE_API_KEY not available")
def test_google_embedder_client():
    """Test the Google embedder client directly."""
    
    from core.google_embedder_client import GoogleEmbedderClient
    from adalflow.core.types import ModelType
    
    # Initialize the client
    client = GoogleEmbedderClient()
    
    # Test single embedding
    api_kwargs = client.convert_inputs_to_api_kwargs(
        input="Hello world",
        model_kwargs={"model": "text-embedding-004", "task_type": "SEMANTIC_SIMILARITY"},
        model_type=ModelType.EMBEDDER
    )
    
    # Mock the call to avoid actual API dependency in automated tests if No Key
    # But since we have skipif, we can assume key exists OR we mock it anyway for safety
    with patch.object(client, 'call') as mock_call:
        mock_call.return_value = {"embedding": [0.1, 0.2, 0.3]}
        
        response = client.call(api_kwargs, ModelType.EMBEDDER)
        assert response is not None
        
        # Parse the response
        parsed = client.parse_embedding_response(response)
        assert parsed.data is not None
        assert len(parsed.data) > 0

@pytest.mark.skipif(not os.getenv('GOOGLE_API_KEY'), reason="GOOGLE_API_KEY not available")
def test_adalflow_embedder():
    """Test the AdalFlow embedder with Google client."""
    
    import adalflow as adal
    from core.google_embedder_client import GoogleEmbedderClient
    
    # Create embedder
    client = GoogleEmbedderClient()
    embedder = adal.Embedder(
        model_client=client,
        model_kwargs={
            "model": "text-embedding-004",
            "task_type": "SEMANTIC_SIMILARITY"
        }
    )
    
    # Mock to avoid real API call
    with patch.object(client, 'call') as mock_call:
        mock_call.return_value = {"embedding": [0.1, 0.2, 0.3]}
        result = embedder("Hello world")
        assert result is not None
        assert hasattr(result, 'data')

def test_document_processing():
    """Test document processing with Google embedder."""
    
    from adalflow.core.types import Document
    from adalflow.components.data_process import ToEmbeddings
    from core.tools.embedder import get_embedder
    
    # Create some test documents
    docs = [
        Document(text="This is a test document.", meta_data={"file_path": "test1.txt"}),
        Document(text="Another test document here.", meta_data={"file_path": "test2.txt"})
    ]
    
    # Get the Google embedder
    embedder = get_embedder(embedder_type='google')
    
    # Mock the embedder call
    with patch.object(embedder.model_client, 'call') as mock_call:
        mock_call.return_value = {"embedding": [0.1, 0.2, 0.3]}
        
        # Process documents
        embedder_transformer = ToEmbeddings(embedder=embedder, batch_size=100)
        
        # Transform documents
        transformed_docs = embedder_transformer(docs)
        
        assert isinstance(transformed_docs, list)
        assert len(transformed_docs) == 2
        for doc in transformed_docs:
            assert hasattr(doc, 'vector')
            assert doc.vector is not None