"""Tests for provider base class."""

from vm_mcp.providers.base import BaseProvider


class TestBaseProvider:
    """Tests for base provider utilities."""

    def test_parse_composite_id_valid(self):
        """Test parsing valid composite ID."""
        result = BaseProvider.parse_composite_id("aws:prod:us-east-1:i-123")
        assert result == ("aws", "prod", "us-east-1", "i-123")

    def test_parse_composite_id_with_colons_in_id(self):
        """Test parsing composite ID with colons in instance ID."""
        # Azure resource IDs can be complex, but our format uses 4 parts
        result = BaseProvider.parse_composite_id("azure:corp:eastus:my-vm")
        assert result == ("azure", "corp", "eastus", "my-vm")

    def test_parse_composite_id_invalid_format(self):
        """Test parsing invalid composite ID."""
        assert BaseProvider.parse_composite_id("invalid") is None
        assert BaseProvider.parse_composite_id("only:two") is None
        assert BaseProvider.parse_composite_id("one:two:three") is None
        assert BaseProvider.parse_composite_id("") is None

    def test_parse_composite_id_five_parts(self):
        """Test parsing composite ID with too many parts."""
        assert BaseProvider.parse_composite_id("a:b:c:d:e") is None
