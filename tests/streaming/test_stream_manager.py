"""
Tests for the StreamManager class.
"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock

import aiohttp
from aiohttp import WSMsgType
from pydantic import ValidationError

from src.streaming.stream_manager import StreamManager
from src.ts_types.config import ClientConfig
from src.utils.token_manager import TokenManager

# Filter out all AsyncMock coroutine warnings - these are expected in testing
pytestmark = pytest.mark.filterwarnings("ignore::RuntimeWarning")


class MockWebSocketResponse:
    """Mock WebSocket response for testing."""

    def __init__(self, data, msg_type=WSMsgType.TEXT):
        self.data = data
        self.type = msg_type

    async def receive(self):
        return self


@pytest.fixture
def mock_token_manager():
    """Mock TokenManager that returns a test token."""
    token_manager = AsyncMock(spec=TokenManager)
    token_manager.get_valid_access_token.return_value = "test_token"
    return token_manager


@pytest.fixture
def stream_manager(mock_token_manager):
    """Create a StreamManager with a mock TokenManager."""
    config = ClientConfig(max_concurrent_streams=5)
    manager = StreamManager(token_manager=mock_token_manager, config=config)
    return manager


@pytest.fixture(autouse=True)
async def cleanup_after_test(stream_manager):
    """Fixture to clean up after each test."""
    yield

    # Cancel any active tasks (use MagicMocks that don't need awaiting)
    for task_dict in [stream_manager._reconnection_tasks, stream_manager._message_processing_tasks]:
        for task in list(task_dict.values()):
            if hasattr(task, "done") and callable(task.done) and not task.done():
                # Use cancel method that doesn't return a coroutine
                if hasattr(task, "cancel") and callable(task.cancel):
                    task.cancel()
        task_dict.clear()

    # Reset states
    stream_manager._active_streams.clear()
    stream_manager._connections.clear()
    stream_manager._subscription_callbacks.clear()


@pytest.mark.asyncio
async def test_connect_stream_success(stream_manager):
    """Test successful connection to a stream."""
    # Mock the WebSocket connection and session
    mock_ws = MagicMock()  # Use MagicMock instead of AsyncMock
    mock_session = MagicMock()

    # Make ws_connect a proper AsyncMock that returns a value
    mock_ws_connect = AsyncMock()
    mock_ws_connect.return_value = mock_ws
    mock_session.ws_connect = mock_ws_connect

    # Mock create_task to return a MagicMock (not AsyncMock)
    process_task = MagicMock()
    process_task.done.return_value = False
    process_task.cancel = MagicMock()  # Regular MagicMock, not AsyncMock

    # Mock the event loop time
    mock_time = 12345.0

    # Create a mock loop with time() that returns a value not a coroutine
    mock_loop = MagicMock()
    mock_loop.time = MagicMock(return_value=mock_time)

    with (
        patch("aiohttp.ClientSession", return_value=mock_session),
        patch("asyncio.create_task", return_value=process_task),
        patch("asyncio.get_event_loop", return_value=mock_loop),
        # Mock _process_messages to be a MagicMock that returns None
        patch.object(stream_manager, "_process_messages", return_value=None),
    ):
        # Connect to a test stream
        await stream_manager.connect_stream("/test/stream", "test_stream")

        # Verify the connection was established
        mock_session.ws_connect.assert_called_once()
        assert "test_stream" in stream_manager._connections
        assert stream_manager._connections["test_stream"]["active"] is True
        assert stream_manager._connections["test_stream"]["last_heartbeat"] == mock_time
        assert "test_stream" in stream_manager._active_streams
        assert stream_manager._message_processing_tasks["test_stream"] == process_task

        # Manual cleanup to avoid affecting other tests
        stream_manager._connections["test_stream"]["active"] = False
        stream_manager._active_streams.remove("test_stream")
        if "test_stream" in stream_manager._message_processing_tasks:
            del stream_manager._message_processing_tasks["test_stream"]


@pytest.mark.asyncio
async def test_connect_stream_already_connected(stream_manager):
    """Test connecting to an already connected stream."""
    # Mock the WebSocket connection and session
    mock_ws = MagicMock()
    mock_session = MagicMock()

    # Make ws_connect a proper AsyncMock that returns a value
    mock_ws_connect = AsyncMock()
    mock_ws_connect.return_value = mock_ws
    mock_session.ws_connect = mock_ws_connect

    # Mock create_task to return a MagicMock (not AsyncMock)
    process_task = MagicMock()

    with (
        patch("aiohttp.ClientSession", return_value=mock_session),
        patch("asyncio.create_task", return_value=process_task),
        patch.object(stream_manager, "_process_messages", return_value=None),
    ):
        # Connect to a test stream
        await stream_manager.connect_stream("/test/stream", "test_stream")

        # Try to connect again to the same stream
        await stream_manager.connect_stream("/test/stream", "test_stream")

        # Verify the connection was only established once
        mock_session.ws_connect.assert_called_once()


@pytest.mark.asyncio
async def test_connect_stream_maximum_limit(stream_manager):
    """Test that connecting more streams than the maximum limit raises an error."""
    # Mock the WebSocket connection and session
    mock_ws = MagicMock()
    mock_session = MagicMock()

    # Make ws_connect a proper AsyncMock that returns a value
    mock_ws_connect = AsyncMock()
    mock_ws_connect.return_value = mock_ws
    mock_session.ws_connect = mock_ws_connect

    # Mock create_task to return a MagicMock (not AsyncMock)
    process_task = MagicMock()

    with (
        patch("aiohttp.ClientSession", return_value=mock_session),
        patch("asyncio.create_task", return_value=process_task),
        patch.object(stream_manager, "_process_messages", return_value=None),
    ):
        # Connect to 5 streams (the maximum)
        for i in range(5):
            await stream_manager.connect_stream(f"/test/stream{i}", f"test_stream{i}")

        # Try to connect to a 6th stream, which should raise ValueError
        with pytest.raises(ValueError, match="Maximum concurrent streams limit reached"):
            await stream_manager.connect_stream("/test/stream6", "test_stream6")


@pytest.mark.asyncio
async def test_connect_stream_connection_error(stream_manager):
    """Test that a connection error is properly handled."""
    # Mock the session to raise an error on connection
    mock_session = MagicMock()

    # Make ws_connect a proper AsyncMock that raises an exception
    mock_ws_connect = AsyncMock(side_effect=aiohttp.ClientError("Connection failed"))
    mock_session.ws_connect = mock_ws_connect

    with patch("aiohttp.ClientSession", return_value=mock_session):
        # Try to connect, which should raise ConnectionError
        with pytest.raises(ConnectionError, match="Failed to connect to stream"):
            await stream_manager.connect_stream("/test/stream", "test_stream")


@pytest.mark.asyncio
async def test_disconnect_stream_success(stream_manager):
    """Test successful disconnection from a stream."""
    # Mock the WebSocket connection and session
    mock_ws = MagicMock()
    mock_session = MagicMock()

    # Need to use AsyncMock for the close methods that will be awaited
    mock_ws_close = AsyncMock()
    mock_session_close = AsyncMock()
    mock_ws.close = mock_ws_close
    mock_session.close = mock_session_close

    # Make ws_connect a proper AsyncMock that returns a value
    mock_ws_connect = AsyncMock()
    mock_ws_connect.return_value = mock_ws
    mock_session.ws_connect = mock_ws_connect

    # Mock create_task to return a MagicMock (not AsyncMock)
    process_task = MagicMock()
    process_task.done.return_value = False
    process_task.cancel = MagicMock()  # Not AsyncMock

    with (
        patch("aiohttp.ClientSession", return_value=mock_session),
        patch("asyncio.create_task", return_value=process_task),
        patch.object(stream_manager, "_process_messages", return_value=None),
    ):
        # Connect to a test stream
        await stream_manager.connect_stream("/test/stream", "test_stream")

        # Add the task to the tracked tasks
        stream_manager._message_processing_tasks["test_stream"] = process_task

        # Disconnect from the stream
        await stream_manager.disconnect_stream("test_stream")

        # Verify the stream was disconnected
        mock_ws_close.assert_called_once()
        mock_session_close.assert_called_once()
        process_task.cancel.assert_called_once()
        assert not stream_manager.is_connected("test_stream")
        assert "test_stream" not in stream_manager._active_streams


@pytest.mark.asyncio
async def test_disconnect_nonexistent_stream(stream_manager):
    """Test disconnecting from a stream that doesn't exist."""
    # Try to disconnect from a stream that doesn't exist
    await stream_manager.disconnect_stream("nonexistent_stream")

    # No assertions needed, just checking that no error is raised


@pytest.mark.asyncio
async def test_disconnect_all_streams(stream_manager):
    """Test disconnecting from all streams."""
    # Create mock websockets and sessions with AsyncMock close methods
    streams = {}
    for i in range(3):
        stream_id = f"test_stream{i}"
        mock_ws = MagicMock()
        mock_session = MagicMock()

        # Use AsyncMock for close methods
        mock_ws.close = AsyncMock()
        mock_session.close = AsyncMock()

        # Set up the connections in the stream manager directly
        stream_manager._connections[stream_id] = {
            "websocket": mock_ws,
            "session": mock_session,
            "active": True,
            "uri": f"/test/stream{i}",
            "last_heartbeat": 0,
        }
        stream_manager._active_streams.add(stream_id)

        # Create a mock task
        process_task = MagicMock()
        process_task.done.return_value = False
        process_task.cancel = MagicMock()
        stream_manager._message_processing_tasks[stream_id] = process_task

        # Store for later assertion
        streams[stream_id] = {"websocket": mock_ws, "session": mock_session, "task": process_task}

    # Disconnect from all streams
    await stream_manager.disconnect_all()

    # Verify all streams were disconnected
    for stream_id, mocks in streams.items():
        mocks["websocket"].close.assert_called_once()
        mocks["session"].close.assert_called_once()
        mocks["task"].cancel.assert_called_once()

    assert len(stream_manager._active_streams) == 0
    assert len(stream_manager._connections) == 0
    assert len(stream_manager._message_processing_tasks) == 0


@pytest.mark.asyncio
async def test_message_callbacks(stream_manager):
    """Test adding and removing message callbacks."""
    # Create some test callbacks
    callback1 = MagicMock()
    callback2 = MagicMock()

    # Add the callbacks to a stream
    stream_manager.add_message_callback("test_stream", callback1)
    stream_manager.add_message_callback("test_stream", callback2)

    # Verify callbacks were added
    assert len(stream_manager._subscription_callbacks["test_stream"]) == 2

    # Remove one callback
    stream_manager.remove_message_callback("test_stream", callback1)

    # Verify the callback was removed
    assert len(stream_manager._subscription_callbacks["test_stream"]) == 1
    assert callback2 in stream_manager._subscription_callbacks["test_stream"]


@pytest.mark.asyncio
async def test_process_text_message(stream_manager):
    """Test processing text messages."""
    # Setup mock connection
    mock_ws = MagicMock()
    mock_session = MagicMock()

    # Mock the event loop time
    mock_time = 12345.0

    # Create a mock loop with time() that returns a value not a coroutine
    mock_loop = MagicMock()
    mock_loop.time = MagicMock(return_value=mock_time)

    with patch("asyncio.get_event_loop", return_value=mock_loop):
        stream_manager._connections = {
            "test_stream": {
                "websocket": mock_ws,
                "session": mock_session,
                "active": True,
                "uri": "/test/stream",
                "last_heartbeat": mock_time,
            }
        }
        stream_manager._active_streams.add("test_stream")

        # Add a test callback
        callback = MagicMock()
        stream_manager.add_message_callback("test_stream", callback)

        # Create a test message
        test_message = {"Symbol": "AAPL", "Price": "150.00"}

        # Process the message
        await stream_manager._handle_text_message("test_stream", json.dumps(test_message))

        # Verify the callback was called with the message
        callback.assert_called_once_with(test_message)


@pytest.mark.asyncio
async def test_process_heartbeat_message(stream_manager):
    """Test processing a heartbeat message."""
    # Setup mock connection
    mock_ws = MagicMock()
    mock_session = MagicMock()

    # Initial and updated heartbeat times
    initial_time = 1000.0
    updated_time = 2000.0

    stream_manager._connections = {
        "test_stream": {
            "websocket": mock_ws,
            "session": mock_session,
            "active": True,
            "uri": "/test/stream",
            "last_heartbeat": initial_time,
        }
    }
    stream_manager._active_streams.add("test_stream")

    # Create a heartbeat message
    heartbeat_message = {"Heartbeat": 123, "Timestamp": "2023-01-01T12:00:00Z"}

    # Create a mock loop with time() that returns a value not a coroutine
    mock_loop = MagicMock()
    mock_loop.time = MagicMock(return_value=updated_time)

    # Mock the event loop time to return a specific value for verification
    with patch("asyncio.get_event_loop", return_value=mock_loop):
        # Process the heartbeat message
        await stream_manager._handle_text_message("test_stream", json.dumps(heartbeat_message))

        # Verify the last_heartbeat was updated
        assert stream_manager._connections["test_stream"]["last_heartbeat"] == updated_time


@pytest.mark.asyncio
async def test_process_error_message(stream_manager):
    """Test processing an error message."""
    # Setup mock connection
    mock_ws = MagicMock()
    mock_session = MagicMock()

    # Mock the event loop time
    mock_time = 12345.0

    # Create a mock loop with time() that returns a value not a coroutine
    mock_loop = MagicMock()
    mock_loop.time = MagicMock(return_value=mock_time)

    with patch("asyncio.get_event_loop", return_value=mock_loop):
        stream_manager._connections = {
            "test_stream": {
                "websocket": mock_ws,
                "session": mock_session,
                "active": True,
                "uri": "/test/stream",
                "last_heartbeat": mock_time,
            }
        }
        stream_manager._active_streams.add("test_stream")

        # Create an error message
        error_message = {"Error": "TestError", "Message": "This is a test error"}

        # Process the error message
        with patch("streaming.stream_manager.logger.error") as mock_logger:
            await stream_manager._handle_text_message("test_stream", json.dumps(error_message))

            # Verify the error was logged
            mock_logger.assert_called_once()
            assert "TestError" in mock_logger.call_args[0][0]


@pytest.mark.asyncio
async def test_process_invalid_json(stream_manager):
    """Test processing invalid JSON."""
    # Setup mock connection
    mock_ws = MagicMock()
    mock_session = MagicMock()

    # Mock the event loop time
    mock_time = 12345.0

    # Create a mock loop with time() that returns a value not a coroutine
    mock_loop = MagicMock()
    mock_loop.time = MagicMock(return_value=mock_time)

    with patch("asyncio.get_event_loop", return_value=mock_loop):
        stream_manager._connections = {
            "test_stream": {
                "websocket": mock_ws,
                "session": mock_session,
                "active": True,
                "uri": "/test/stream",
                "last_heartbeat": mock_time,
            }
        }
        stream_manager._active_streams.add("test_stream")

        # Create invalid JSON
        invalid_json = "{not valid json"

        # Process the invalid JSON
        with patch("streaming.stream_manager.logger.error") as mock_logger:
            await stream_manager._handle_text_message("test_stream", invalid_json)

            # Verify the error was logged
            mock_logger.assert_called_once()
            assert "Invalid JSON" in mock_logger.call_args[0][0]


@pytest.mark.asyncio
async def test_process_messages_reconnect(stream_manager):
    """Test that a disconnected stream attempts to reconnect."""
    # Setup mock connection with MagicMock (not AsyncMock)
    mock_ws = MagicMock()

    # Make receive return an async function that returns the mock responses
    mock_responses = [
        MockWebSocketResponse(json.dumps({"data": "test"})),
        MockWebSocketResponse(None, WSMsgType.CLOSED),  # Simulate connection close
    ]

    async def mock_receive():
        return mock_responses.pop(0)

    mock_ws.receive = mock_receive
    mock_session = MagicMock()

    # Mock the event loop time
    mock_time = 12345.0

    # Create a mock loop with time() that returns a value not a coroutine
    mock_loop = MagicMock()
    mock_loop.time = MagicMock(return_value=mock_time)

    # Mock asyncio.wait_for to immediately return the next mock response
    async def mock_wait_for(coro, timeout):
        return await coro

    # Create a MagicMock task for reconnection
    reconnect_task = MagicMock()

    with (
        patch("asyncio.get_event_loop", return_value=mock_loop),
        patch("asyncio.wait_for", mock_wait_for),
        patch.object(stream_manager, "_attempt_reconnection") as mock_reconnect,
        patch("asyncio.create_task", return_value=reconnect_task),
    ):
        stream_manager._connections = {
            "test_stream": {
                "websocket": mock_ws,
                "session": mock_session,
                "active": True,
                "uri": "/test/stream",
                "last_heartbeat": mock_time,
            }
        }
        stream_manager._active_streams.add("test_stream")

        # Mock _handle_text_message to avoid coroutine issues
        stream_manager._handle_text_message = AsyncMock()

        # Process messages until connection closes
        await stream_manager._process_messages("test_stream")

        # Verify reconnection was attempted
        mock_reconnect.assert_called_once_with("test_stream")


@pytest.mark.asyncio
async def test_reconnect_with_backoff_success(stream_manager):
    """Test successful reconnection with backoff."""
    # Setup original connection
    mock_ws = MagicMock()
    mock_session = MagicMock()

    # Mock the event loop time
    mock_time = 12345.0

    # Create a mock loop with time() that returns a value not a coroutine
    mock_loop = MagicMock()
    mock_loop.time = MagicMock(return_value=mock_time)

    with patch("asyncio.get_event_loop", return_value=mock_loop):
        stream_manager._connections = {
            "test_stream": {
                "websocket": mock_ws,
                "session": mock_session,
                "active": True,
                "uri": "/test/stream",
                "last_heartbeat": mock_time,
            }
        }

        # Mock connect_stream to succeed on first attempt
        connect_mock = AsyncMock()

        with (
            patch.object(stream_manager, "connect_stream", connect_mock),
            patch("asyncio.sleep", AsyncMock()),  # Skip the delay
        ):
            # Attempt reconnection
            await stream_manager._reconnect_with_backoff("test_stream")

            # Verify connect_stream was called once (first attempt succeeded)
            connect_mock.assert_called_once_with("/test/stream", "test_stream")


@pytest.mark.asyncio
async def test_reconnect_with_backoff_failure(stream_manager):
    """Test failed reconnection with backoff."""
    # Setup original connection
    mock_ws = MagicMock()
    mock_session = MagicMock()

    # Mock the event loop time
    mock_time = 12345.0

    # Create a mock loop with time() that returns a value not a coroutine
    mock_loop = MagicMock()
    mock_loop.time = MagicMock(return_value=mock_time)

    with patch("asyncio.get_event_loop", return_value=mock_loop):
        stream_manager._connections = {
            "test_stream": {
                "websocket": mock_ws,
                "session": mock_session,
                "active": True,
                "uri": "/test/stream",
                "last_heartbeat": mock_time,
            }
        }

        # Set the max attempts to a small number for testing
        stream_manager._MAX_RECONNECT_ATTEMPTS = 2

        # Mock connect_stream to always fail
        connect_mock = AsyncMock(side_effect=ConnectionError("Test connection error"))

        with (
            patch.object(stream_manager, "connect_stream", connect_mock),
            patch("asyncio.sleep", AsyncMock()),  # Skip the delay
            patch("streaming.stream_manager.logger.error") as mock_logger,
        ):
            # Attempt reconnection
            await stream_manager._reconnect_with_backoff("test_stream")

            # Verify connect_stream was called twice (max attempts)
            assert connect_mock.call_count == 2

            # Verify the failure was logged
            mock_logger.assert_called()
            assert any("Failed to reconnect" in call[0][0] for call in mock_logger.call_args_list)

            # Verify the connection is marked as inactive
            assert not stream_manager._connections["test_stream"]["active"]


@pytest.mark.asyncio
async def test_is_connected(stream_manager):
    """Test the is_connected method."""
    # Setup connection
    mock_ws = MagicMock()
    mock_session = MagicMock()
    stream_manager._connections = {
        "active_stream": {
            "websocket": mock_ws,
            "session": mock_session,
            "active": True,
            "uri": "/test/stream",
            "last_heartbeat": 0,
        },
        "inactive_stream": {
            "websocket": mock_ws,
            "session": mock_session,
            "active": False,
            "uri": "/test/stream",
            "last_heartbeat": 0,
        },
    }
    stream_manager._active_streams.add("active_stream")

    # Check connection status
    assert stream_manager.is_connected("active_stream")
    assert not stream_manager.is_connected("inactive_stream")
    assert not stream_manager.is_connected("nonexistent_stream")


@pytest.mark.asyncio
async def test_get_connection_status(stream_manager):
    """Test the get_connection_status method."""
    # Setup connections
    mock_ws = MagicMock()
    mock_session = MagicMock()
    stream_manager._connections = {
        "active_stream": {
            "websocket": mock_ws,
            "session": mock_session,
            "active": True,
            "uri": "/test/stream",
            "last_heartbeat": 0,
        },
        "inactive_stream": {
            "websocket": mock_ws,
            "session": mock_session,
            "active": False,
            "uri": "/test/stream",
            "last_heartbeat": 0,
        },
    }
    stream_manager._active_streams.add("active_stream")

    # Get connection status
    status = stream_manager.get_connection_status()

    # Verify the status
    assert status["active_stream"]
    assert not status["inactive_stream"]
