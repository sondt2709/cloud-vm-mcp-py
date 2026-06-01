"""User confirmation gate for state-changing tools via MCP elicitation.

Mirrors the pattern used by mongodb-mcp-server: a tool that mutates state asks
the connected client to confirm before acting. Confirmation uses the standard
MCP elicitation primitive (``Context.elicit``), so it works in any
elicitation-capable client. When the client does not support elicitation, the
gate fails open (allows the action) to preserve compatibility with
non-interactive clients.
"""

import logging

from mcp.server.fastmcp import Context
from mcp.types import ClientCapabilities, ElicitationCapability
from pydantic import BaseModel, Field

from vm_mcp.config import get_confirm_required_tools

logger = logging.getLogger(__name__)


class Confirm(BaseModel):
    """Single Yes/No field collected from the user during confirmation.

    A field is mandatory: the MCP SDK only registers an ``accept`` action when
    the response carries non-empty content (``elicit_with_validation`` treats
    ``accept`` + empty content as an error), so an empty schema cannot work.

    The annotation must be a primitive type — ``Literal[...]`` is rejected by
    the SDK's ``_validate_elicitation_schema`` — so the Yes/No constraint is
    applied via the JSON Schema ``enum`` on a plain ``str``.
    """

    confirmation: str = Field(
        description="Confirm the action?",
        json_schema_extra={"enum": ["Yes", "No"]},
    )


def requires_confirmation(tool_name: str) -> bool:
    """Return whether the named tool requires user confirmation."""
    return tool_name in get_confirm_required_tools()


def supports_elicitation(ctx: Context) -> bool:
    """Return whether the connected client advertises elicitation capability."""
    try:
        return ctx.session.check_client_capability(
            ClientCapabilities(elicitation=ElicitationCapability())
        )
    except Exception:
        # If capability cannot be determined, treat as unsupported (fail-open).
        logger.exception("Failed to check client elicitation capability")
        return False


async def confirm(ctx: Context, message: str) -> bool:
    """Request a yes/no confirmation from the user.

    Returns ``True`` if the action may proceed:
    - the client does not support elicitation (fail-open), or
    - the user accepts the prompt and answers "Yes".

    Returns ``False`` if the user declines, cancels, or the prompt otherwise
    does not produce an explicit "Yes".
    """
    if not supports_elicitation(ctx):
        return True

    try:
        result = await ctx.elicit(message=message, schema=Confirm)
    except Exception:
        # On any elicitation error/timeout, do not proceed with the action.
        logger.exception("Elicitation request failed")
        return False

    return result.action == "accept" and result.data is not None and result.data.confirmation == "Yes"
