import logging
import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

BASE_URL = "https://api.github.com"


class GitHubAPIError(Exception):
    """Raised when the GitHub API call cannot be completed."""


class GitHubClient:
    def __init__(self, token=None, max_retries=3, max_rate_limit_wait=300):
        token = token or os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError("No GitHub token found. Check your .env file.")

        self.max_retries = max_retries
        self.max_rate_limit_wait = max_rate_limit_wait
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

    def get(self, path, params=None):
        """GET one URL. Returns the response, or None if the page is not found."""
        url = path if path.startswith("http") else f"{BASE_URL}{path}"

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.get(url, params=params, timeout=30)
            except requests.RequestException as exc:
                logger.warning("Network error on %s (attempt %s): %s", url, attempt, exc)
                self._pause(attempt)
                continue

            status = response.status_code

            if status == 200:
                remaining = response.headers.get("X-RateLimit-Remaining")
                logger.debug("OK %s (requests left: %s)", url, remaining)
                return response

            if status == 404:
                logger.warning("Not found, skipping: %s", url)
                return None

            if status == 401:
                raise GitHubAPIError("401 Unauthorized. Check your token.")

            if status in (403, 429):
                self._wait_for_rate_limit(response)
                continue

            if status >= 500:
                logger.warning("Server error %s on %s (attempt %s)", status, url, attempt)
                self._pause(attempt)
                continue

            raise GitHubAPIError(f"Unexpected status {status} for {url}")

        raise GitHubAPIError(f"Gave up on {url} after {self.max_retries} attempts")

    def get_paginated(self, path, params=None, max_pages=None):
        """Yield every item across all pages of a list endpoint."""
        params = dict(params or {})
        params.setdefault("per_page", 100)
        url = path
        pages = 0

        while url and (max_pages is None or pages < max_pages):
            response = self.get(url, params=params)
            if response is None:
                return
            yield from response.json()
            pages += 1
            url = response.links.get("next", {}).get("url")
            params = None  # the next URL already contains the settings

    def _pause(self, attempt):
        delay = 2**attempt  # 2s, 4s, 8s
        logger.info("Waiting %s seconds before retrying", delay)
        time.sleep(delay)

    def _wait_for_rate_limit(self, response):
        retry_after = response.headers.get("Retry-After")
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset = response.headers.get("X-RateLimit-Reset")

        if retry_after:
            wait = int(retry_after)
        elif remaining == "0" and reset:
            wait = max(int(reset) - int(time.time()), 1)
        else:
            raise GitHubAPIError(f"403 Forbidden: {response.text[:200]}")

        if wait > self.max_rate_limit_wait:
            raise GitHubAPIError(f"Rate limit resets in {wait}s, which is too long to wait")

        logger.warning("Rate limited. Waiting %s seconds", wait)
        time.sleep(wait + 1)