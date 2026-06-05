"""Simple token-based authentication."""

import secrets
import hashlib
from mcp.server.auth.provider import AccessToken
from .config import AUTH_TOKEN


def validate_token(token: str) -> dict | None:
    """Validate a Bearer token. Returns team info dict or None."""
    if AUTH_TOKEN and token == AUTH_TOKEN:
        return {"team_id": "dev-team", "team_name": "Development"}

    if token:
        team_hash = hashlib.sha256(token.encode()).hexdigest()[:8]
        return {"team_id": f"team-{team_hash}", "team_name": f"Team {team_hash}"}

    return None


def generate_token() -> str:
    """Generate a new random token."""
    return secrets.token_urlsafe(32)


async def token_verifier(token: str) -> AccessToken | None:
    """FastMCP TokenVerifier protocol — validates Bearer tokens.

    Called by FastMCP on every request when token_verifier is set.
    Returns AccessToken if valid, None to reject.
    """
    team = validate_token(token)
    if team is None:
        return None

    return AccessToken(
        token=token,
        client_id=team["team_id"],
        scopes=["openclaw:task"],
    )
