"""Tests for AgentService."""

import pytest
from unittest.mock import MagicMock, patch

from services.agent_service import AgentService
from schemas.agent import LegalType, CompanySize


@pytest.fixture
def mock_config_loader():
    """Mock config loader."""
    loader = MagicMock()
    loader.load_all_configs.return_value = [
        MagicMock(
            id="agent-1",
            company_name="Test Company 1",
            legal_type=LegalType.OOO,
            industry="IT",
            size=CompanySize.SMB,
            region="Moscow",
        ),
        MagicMock(
            id="agent-2",
            company_name="Test Company 2",
            legal_type=LegalType.IP,
            industry="Retail",
            size=CompanySize.MICRO,
            region="SPb",
        ),
    ]
    loader.list_available_agents.return_value = ["agent-1", "agent-2"]
    return loader


@pytest.fixture
def agent_service(mock_config_loader):
    """Create agent service with mock loader."""
    return AgentService(config_loader=mock_config_loader)


@pytest.mark.asyncio
async def test_list_agents(agent_service, mock_config_loader):
    """Test listing agents."""
    db = MagicMock()
    org_id = MagicMock()

    items, total = await agent_service.list_agents(db, org_id, page=1, limit=10)

    assert total == 2
    assert len(items) == 2
    assert items[0].id == "agent-1"
    assert items[1].id == "agent-2"


@pytest.mark.asyncio
async def test_list_agents_with_filter(agent_service, mock_config_loader):
    """Test listing agents with industry filter."""
    db = MagicMock()
    org_id = MagicMock()

    items, total = await agent_service.list_agents(
        db, org_id, page=1, limit=10, industry="IT"
    )

    mock_config_loader.load_all_configs.assert_called()


@pytest.mark.asyncio
async def test_validate_agent_ids(agent_service, mock_config_loader):
    """Test validating agent IDs."""
    invalid = await agent_service.validate_agent_ids(["agent-1", "invalid-agent"])

    assert "invalid-agent" in invalid
    assert "agent-1" not in invalid
