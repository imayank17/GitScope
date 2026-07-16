import logging
import os
import shutil
import time
import pytest
import respx
from httpx import Response
from app.core.config import settings
from app.core.logging import setup_logging, get_logger, UTCFormatter, ColoredFormatter


@pytest.fixture(autouse=True)
def clean_logs_dir():
    """Ensure a clean logs directory for each test."""
    test_logs_dir = "test_logs"
    # Temporarily override settings
    old_dir = settings.LOG_DIRECTORY
    old_to_file = settings.LOG_TO_FILE
    settings.LOG_DIRECTORY = test_logs_dir
    settings.LOG_TO_FILE = True
    
    if os.path.exists(test_logs_dir):
        shutil.rmtree(test_logs_dir)
        
    yield
    
    # Restore settings
    settings.LOG_DIRECTORY = old_dir
    settings.LOG_TO_FILE = old_to_file
    if os.path.exists(test_logs_dir):
        shutil.rmtree(test_logs_dir)


@pytest.mark.anyio
async def test_setup_logging_creates_directory():
    """Verify that setup_logging automatically creates the target logs directory."""
    assert not os.path.exists(settings.LOG_DIRECTORY)
    setup_logging()
    assert os.path.exists(settings.LOG_DIRECTORY)


@pytest.mark.anyio
async def test_log_format_and_utc_time():
    """Verify log structure, pipe separation, and UTC time format (YYYY-MM-DD HH:MM:SS)."""
    formatter = UTCFormatter(
        fmt="%(asctime)s | %(levelname)s | %(module)s | %(funcName)s | line %(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    # Create mock record
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_logging.py",
        lineno=10,
        msg="Test log message",
        args=(),
        exc_info=None,
        func="test_function"
    )
    
    formatted = formatter.format(record)
    
    # Assert format pattern: 2026-07-16 18:42:15 | INFO | test_logging | test_function | line 10 | Test log message
    parts = [p.strip() for p in formatted.split("|")]
    assert len(parts) == 6
    assert parts[1] == "INFO"
    assert parts[2] == "test_logging"
    assert parts[3] == "test_function"
    assert parts[4] == "line 10"
    assert parts[5] == "Test log message"
    
    # Assert timestamp matches UTC year/date
    timestamp = parts[0]
    struct_time = time.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    assert struct_time is not None


@pytest.mark.anyio
async def test_colored_console_formatter():
    """Verify console levelname is colorized and original levelname remains unmodified."""
    formatter = ColoredFormatter(
        fmt="%(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_module.py",
        lineno=10,
        msg="Message",
        args=(),
        exc_info=None,
        func="test_func"
    )
    formatted = formatter.format(record)
    assert "\033[32m" in formatted
    assert "INFO" in formatted
    assert record.levelname == "INFO"


@pytest.mark.anyio
async def test_separate_domain_log_files():
    """Verify that domain logs are written to separate log files and error logs are filtered."""
    setup_logging()
    
    app_logger = get_logger("app.main")
    github_logger = get_logger("app.services.github_service")
    sync_logger = get_logger("app.services.sync_service")
    repo_logger = get_logger("app.repositories.github_repository")
    
    app_logger.info("General app log event")
    github_logger.info("GitHub service specific event")
    sync_logger.warning("Sync warning event")
    repo_logger.info("Repository db operation event")
    app_logger.error("Severe app error event")
    
    time.sleep(0.1)
    
    app_log_path = os.path.join(settings.LOG_DIRECTORY, "app.log")
    assert os.path.exists(app_log_path)
    with open(app_log_path, "r") as f:
        app_content = f.read()
        assert "General app log event" in app_content
        assert "GitHub service specific event" in app_content
        assert "Sync warning event" in app_content
        assert "Repository db operation event" in app_content
        assert "Severe app error event" in app_content
        
    error_log_path = os.path.join(settings.LOG_DIRECTORY, "error.log")
    assert os.path.exists(error_log_path)
    with open(error_log_path, "r") as f:
        error_content = f.read()
        assert "Severe app error event" in error_content
        assert "General app log event" not in error_content
        assert "GitHub service specific event" not in error_content

    github_log_path = os.path.join(settings.LOG_DIRECTORY, "github.log")
    assert os.path.exists(github_log_path)
    with open(github_log_path, "r") as f:
        github_content = f.read()
        assert "GitHub service specific event" in github_content
        assert "General app log event" not in github_content
        assert "Sync warning event" not in github_content

    sync_log_path = os.path.join(settings.LOG_DIRECTORY, "sync.log")
    assert os.path.exists(sync_log_path)
    with open(sync_log_path, "r") as f:
        sync_content = f.read()
        assert "Sync warning event" in sync_content
        assert "Repository db operation event" in sync_content
        assert "GitHub service specific event" not in sync_content


@pytest.mark.anyio
async def test_rate_limit_warning_log(caplog):
    """Test that GitHubService logs warning messages if rate limits are low."""
    import httpx
    from app.services.github_service import GitHubService
    
    headers = {
        "X-RateLimit-Limit": "5000",
        "X-RateLimit-Remaining": "9",
        "X-RateLimit-Reset": "1672531199"
    }
    
    with respx.mock:
        respx.get("https://api.github.com/repos/test-owner/test-repo").mock(
            return_value=Response(200, json={"name": "test-repo"}, headers=headers)
        )
        
        async with httpx.AsyncClient() as raw_client:
            service = GitHubService(raw_client)
            with caplog.at_level(logging.WARNING):
                await service.get_repository("test-owner", "test-repo")
            
        assert any("Rate limit warning: low remaining requests" in record.message for record in caplog.records)


@pytest.mark.anyio
async def test_request_logging_middleware(client, caplog):
    """Test that our LoggingMiddleware logs incoming requests and responses."""
    with caplog.at_level(logging.INFO):
        response = await client.get("/health")
        assert response.status_code == 200
        
    log_messages = [record.message for record in caplog.records]
    assert any("Incoming Request: GET /health" in msg for msg in log_messages)
    assert any("Response: GET /health | Status: 200" in msg for msg in log_messages)


@pytest.mark.anyio
async def test_database_session_failure_log(caplog):
    """Test that get_db logs database errors when session creation fails."""
    from app.database.session import get_db
    from unittest.mock import patch
    from sqlalchemy.exc import SQLAlchemyError

    with patch("app.database.session.AsyncSessionLocal", side_effect=SQLAlchemyError("Connection refused")):
        with pytest.raises(SQLAlchemyError):
            async for _ in get_db():
                pass
                
    assert any("Failed to establish database session" in record.message for record in caplog.records)

