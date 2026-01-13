"""
X API V2 Client
Wrapper for Twitter/X API V2 operations
"""
import requests
from typing import Optional, Dict, List, Any
from datetime import datetime, timezone
from config import XAPIConfig


class XAPIClient:
    """X API V2 Client for fetching user tweets"""

    def __init__(self, bearer_token: Optional[str] = None):
        """
        Initialize X API client

        Args:
            bearer_token: Bearer token for API authentication.
                         If not provided, uses XAPIConfig.BEARER_TOKEN
        """
        self.bearer_token = bearer_token or XAPIConfig.BEARER_TOKEN
        if not self.bearer_token:
            raise ValueError("Bearer token is required")

        self.base_url = XAPIConfig.BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        })

    def get_user_id_by_username(self, username: str) -> Optional[str]:
        """
        Get user ID by username

        Args:
            username: Twitter/X username (without @)

        Returns:
            User ID string or None if not found
        """
        url = f"{self.base_url}/users/by/username/{username}"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get("data", {}).get("id")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to get user ID for @{username}: {e}")
            return None

    def get_user_tweets(
        self,
        user_id: str,
        max_results: int = 10,
        since_id: Optional[str] = None,
        start_time: Optional[str] = None,
        exclude_replies: bool = False,
        exclude_retweets: bool = False
    ) -> Dict[str, Any]:
        """
        Get tweets from a specific user

        Args:
            user_id: Twitter/X user ID
            max_results: Maximum number of tweets to return (5-100)
            since_id: Returns tweets with ID greater than this
            start_time: Returns tweets created after this time (ISO 8601)
            exclude_replies: Exclude reply tweets
            exclude_retweets: Exclude retweets

        Returns:
            Dictionary with tweets data and metadata
        """
        url = f"{self.base_url}/users/{user_id}/tweets"

        params = {
            "max_results": min(max_results, 100),
            "tweet.fields": "id,text,created_at,author_id,public_metrics,entities,referenced_tweets",
            "expansions": "author_id,referenced_tweets.id",
            "user.fields": "id,name,username,verified"
        }

        if since_id:
            params["since_id"] = since_id

        if start_time:
            params["start_time"] = start_time

        # Build excludes list
        excludes = []
        if exclude_replies:
            excludes.append("replies")
        if exclude_retweets:
            excludes.append("retweets")
        if excludes:
            params["exclude"] = ",".join(excludes)

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to fetch tweets: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"[ERROR] Response: {e.response.text}")
            return {"data": [], "meta": {}}

    def get_latest_tweets(
        self,
        username: str,
        max_results: int = 10,
        exclude_replies: bool = True,
        exclude_retweets: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get latest tweets from a user by username

        Args:
            username: Twitter/X username (without @)
            max_results: Maximum number of tweets to return
            exclude_replies: Exclude reply tweets
            exclude_retweets: Exclude retweets

        Returns:
            List of tweet dictionaries
        """
        user_id = self.get_user_id_by_username(username)
        if not user_id:
            return []

        result = self.get_user_tweets(
            user_id=user_id,
            max_results=max_results,
            exclude_replies=exclude_replies,
            exclude_retweets=exclude_retweets
        )

        return result.get("data", [])

    def get_new_tweets_since(
        self,
        user_id: str,
        since_id: str,
        exclude_replies: bool = True,
        exclude_retweets: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get new tweets since a specific tweet ID

        Args:
            user_id: Twitter/X user ID
            since_id: Tweet ID to fetch tweets after
            exclude_replies: Exclude reply tweets
            exclude_retweets: Exclude retweets

        Returns:
            List of new tweet dictionaries
        """
        result = self.get_user_tweets(
            user_id=user_id,
            max_results=100,
            since_id=since_id,
            exclude_replies=exclude_replies,
            exclude_retweets=exclude_retweets
        )

        return result.get("data", [])

    def format_tweet(self, tweet: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format tweet data for easier use

        Args:
            tweet: Raw tweet data from API

        Returns:
            Formatted tweet dictionary
        """
        return {
            "id": tweet.get("id"),
            "text": tweet.get("text"),
            "created_at": tweet.get("created_at"),
            "author_id": tweet.get("author_id"),
            "url": f"https://twitter.com/i/web/status/{tweet.get('id')}",
            "metrics": tweet.get("public_metrics", {}),
            "entities": tweet.get("entities", {}),
            "is_reply": self._is_reply(tweet),
            "is_retweet": self._is_retweet(tweet),
        }

    @staticmethod
    def _is_reply(tweet: Dict[str, Any]) -> bool:
        """Check if tweet is a reply"""
        refs = tweet.get("referenced_tweets", [])
        return any(ref.get("type") == "replied_to" for ref in refs)

    @staticmethod
    def _is_retweet(tweet: Dict[str, Any]) -> bool:
        """Check if tweet is a retweet"""
        refs = tweet.get("referenced_tweets", [])
        return any(ref.get("type") == "retweeted" for ref in refs)
