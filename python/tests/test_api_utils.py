"""
Test suite for api/utils.py
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import httpx

from a2abase.api.utils import stream_from_url


class TestStreamFromUrl:
    """Test class for stream_from_url function"""

    @pytest.mark.asyncio
    async def test_stream_from_url_success(self):
        """Test stream_from_url with successful response"""
        mock_response = AsyncMock()
        mock_response.raise_for_status = Mock()
        mock_line1 = "data: chunk1"
        mock_line2 = "data: chunk2"
        mock_line3 = ""  # Empty line should be skipped
        mock_line4 = "data: chunk3"
        
        async def mock_aiter_lines():
            yield mock_line1
            yield mock_line2
            yield mock_line3
            yield mock_line4
        
        mock_response.aiter_lines = mock_aiter_lines
        
        mock_stream_context = MagicMock()
        mock_stream_context.__aenter__ = AsyncMock(return_value=mock_response)
        mock_stream_context.__aexit__ = AsyncMock(return_value=None)
        
        mock_client = MagicMock()
        mock_client.stream = Mock(return_value=mock_stream_context)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch('a2abase.api.utils.httpx.AsyncClient', return_value=mock_client):
            chunks = []
            async for chunk in stream_from_url("http://example.com/stream"):
                chunks.append(chunk)
            
            assert len(chunks) == 3
            assert chunks[0] == "data: chunk1"
            assert chunks[1] == "data: chunk2"
            assert chunks[2] == "data: chunk3"

    @pytest.mark.asyncio
    async def test_stream_from_url_with_headers(self):
        """Test stream_from_url with custom headers"""
        mock_response = AsyncMock()
        mock_response.raise_for_status = Mock()
        
        async def mock_aiter_lines():
            yield "data: chunk1"
        
        mock_response.aiter_lines = mock_aiter_lines
        
        mock_stream_context = MagicMock()
        mock_stream_context.__aenter__ = AsyncMock(return_value=mock_response)
        mock_stream_context.__aexit__ = AsyncMock(return_value=None)
        
        mock_client = MagicMock()
        mock_client.stream = Mock(return_value=mock_stream_context)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch('a2abase.api.utils.httpx.AsyncClient', return_value=mock_client):
            chunks = []
            async for chunk in stream_from_url("http://example.com/stream", headers={"Authorization": "Bearer token"}):
                chunks.append(chunk)
            
            mock_client.stream.assert_called_once()
            call_kwargs = mock_client.stream.call_args[1]
            assert "headers" in call_kwargs

    @pytest.mark.asyncio
    async def test_stream_from_url_empty_response(self):
        """Test stream_from_url with empty response"""
        mock_response = AsyncMock()
        mock_response.raise_for_status = Mock()
        
        async def mock_aiter_lines():
            return
            yield  # Make it a generator
        
        mock_response.aiter_lines = mock_aiter_lines
        
        mock_stream_context = MagicMock()
        mock_stream_context.__aenter__ = AsyncMock(return_value=mock_response)
        mock_stream_context.__aexit__ = AsyncMock(return_value=None)
        
        mock_client = MagicMock()
        mock_client.stream = Mock(return_value=mock_stream_context)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch('a2abase.api.utils.httpx.AsyncClient', return_value=mock_client):
            chunks = []
            async for chunk in stream_from_url("http://example.com/stream"):
                chunks.append(chunk)
            
            assert len(chunks) == 0

    @pytest.mark.asyncio
    async def test_stream_from_url_skips_empty_lines(self):
        """Test stream_from_url skips empty/whitespace-only lines"""
        mock_response = AsyncMock()
        mock_response.raise_for_status = Mock()
        
        async def mock_aiter_lines():
            yield "  "  # Whitespace only
            yield ""  # Empty
            yield "data: chunk1"
            yield "\t"  # Tab only
        
        mock_response.aiter_lines = mock_aiter_lines
        
        mock_stream_context = MagicMock()
        mock_stream_context.__aenter__ = AsyncMock(return_value=mock_response)
        mock_stream_context.__aexit__ = AsyncMock(return_value=None)
        
        mock_client = MagicMock()
        mock_client.stream = Mock(return_value=mock_stream_context)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch('a2abase.api.utils.httpx.AsyncClient', return_value=mock_client):
            chunks = []
            async for chunk in stream_from_url("http://example.com/stream"):
                chunks.append(chunk)
            
            assert len(chunks) == 1
            assert chunks[0] == "data: chunk1"

    @pytest.mark.asyncio
    async def test_stream_from_url_timeout_configuration(self):
        """Test stream_from_url uses correct timeout configuration"""
        mock_response = AsyncMock()
        mock_response.raise_for_status = Mock()
        
        async def mock_aiter_lines():
            yield "data: chunk1"
        
        mock_response.aiter_lines = mock_aiter_lines
        
        mock_stream_context = MagicMock()
        mock_stream_context.__aenter__ = AsyncMock(return_value=mock_response)
        mock_stream_context.__aexit__ = AsyncMock(return_value=None)
        
        mock_client = MagicMock()
        mock_client.stream = Mock(return_value=mock_stream_context)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch('a2abase.api.utils.httpx.AsyncClient') as mock_client_class:
            mock_client_class.return_value = mock_client
            chunks = []
            async for chunk in stream_from_url("http://example.com/stream"):
                chunks.append(chunk)
            
            # Verify timeout was configured
            call_kwargs = mock_client_class.call_args[1]
            assert "timeout" in call_kwargs
            timeout = call_kwargs["timeout"]
            assert timeout.connect == 30.0
            assert timeout.read == 300.0
            assert timeout.write == 30.0
            assert timeout.pool == 30.0

    @pytest.mark.asyncio
    async def test_stream_from_url_http_error(self):
        """Test stream_from_url raises error on HTTP error"""
        mock_response = AsyncMock()
        mock_response.raise_for_status = Mock(side_effect=httpx.HTTPStatusError("Error", request=Mock(), response=Mock()))
        
        mock_stream_context = MagicMock()
        mock_stream_context.__aenter__ = AsyncMock(return_value=mock_response)
        mock_stream_context.__aexit__ = AsyncMock(return_value=None)
        
        mock_client = MagicMock()
        mock_client.stream = Mock(return_value=mock_stream_context)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch('a2abase.api.utils.httpx.AsyncClient', return_value=mock_client):
            with pytest.raises(httpx.HTTPStatusError):
                async for chunk in stream_from_url("http://example.com/stream"):
                    pass

