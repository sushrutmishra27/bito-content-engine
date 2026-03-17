"""GitHub integration — fetches recent PRs, releases, and activity."""

import logging
from datetime import datetime, timedelta, timezone

import httpx

logger = logging.getLogger(__name__)


class GitHubIngester:
    def __init__(self, token: str, org: str = "gitbito"):
        self.token = token
        self.org = org
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        }

    async def get_recent_prs(self, repo: str, days_back: int = 7) -> str:
        """Fetch merged PRs from the past week."""
        since = (datetime.now(timezone.utc) - timedelta(days=days_back)).isoformat()

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/repos/{self.org}/{repo}/pulls",
                headers=self.headers,
                params={"state": "closed", "sort": "updated", "direction": "desc", "per_page": 50},
            )
            prs = resp.json()

        if not isinstance(prs, list):
            logger.error(f"GitHub API error: {prs}")
            return ""

        merged = [
            pr for pr in prs
            if pr.get("merged_at") and pr["merged_at"] >= since
        ]

        formatted = []
        for pr in merged:
            formatted.append(f"- **{pr['title']}** (#{pr['number']}) by {pr['user']['login']}")

        return "\n".join(formatted)

    async def get_recent_releases(self, repo: str) -> str:
        """Fetch recent releases."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/repos/{self.org}/{repo}/releases",
                headers=self.headers,
                params={"per_page": 5},
            )
            releases = resp.json()

        if not isinstance(releases, list):
            return ""

        formatted = []
        for release in releases:
            formatted.append(f"- **{release['name']}**: {release.get('body', '')[:200]}")

        return "\n".join(formatted)

    async def get_weekly_summary(self, repos: list[str]) -> str:
        """Get combined GitHub activity across repos."""
        parts = []
        for repo in repos:
            prs = await self.get_recent_prs(repo)
            releases = await self.get_recent_releases(repo)
            if prs or releases:
                section = f"### {repo}\n"
                if prs:
                    section += f"**Merged PRs:**\n{prs}\n"
                if releases:
                    section += f"**Releases:**\n{releases}\n"
                parts.append(section)
        return "\n\n".join(parts)
