import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.rag_service import RAGService

@pytest.fixture
def mock_vector_store():
    store = AsyncMock()
    store.search = AsyncMock()
    return store

@pytest.fixture
def mock_llm_service():
    service = AsyncMock()
    service.chat_stream = AsyncMock()
    return service

@pytest.fixture
def rag_service(mock_vector_store, mock_llm_service):
    return RAGService(mock_vector_store, mock_llm_service)

@pytest.mark.asyncio
async def test_get_context(rag_service, mock_vector_store):
    # Setup mock return value
    mock_results = [MagicMock(text="test context 1"), MagicMock(text="test context 2")]
    mock_vector_store.search.return_value = mock_results
    
    # Test context retrieval
    context = await rag_service.get_context("test query")
    
    # Verify results
    assert len(context) == 2
    assert context == ["test context 1", "test context 2"]
    mock_vector_store.search.assert_called_once_with("test query", k=3)

@pytest.mark.asyncio
async def test_generate_response(rag_service, mock_vector_store, mock_llm_service):
    # Setup mocks
    mock_vector_store.search.return_value = [MagicMock(text="test context")]
    mock_llm_service.chat_stream = AsyncMock()
    mock_llm_service.chat_stream.return_value = [token async for token in async_generator(["test", " response"])]
    
    # Test response generation
    response = [token async for token in await rag_service.generate_response("test query")]
    
    # Verify results
    assert response == ["test", " response"]
    mock_vector_store.search.assert_called_once()
    mock_llm_service.chat_stream.assert_called_once()

@pytest.mark.asyncio
async def test_get_response_with_context(rag_service, mock_vector_store, mock_llm_service):
    # Setup mocks
    mock_vector_store.search.return_value = [MagicMock(text="test context")]
    mock_llm_service.chat_stream = AsyncMock()
    mock_llm_service.chat_stream.return_value = [token async for token in async_generator(["test response"])]
    
    # Test response with context
    stream, context = await rag_service.get_response_with_context("test query")
    
    # Verify results
    assert context == ["test context"]
    assert [token async for token in stream] == ["test response"]

async def async_generator(items):
    for item in items:
        yield item
