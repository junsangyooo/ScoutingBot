"""
Tweet Storage Manager
Handles storing and tracking processed tweets
"""
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class TweetStorage:
    """Manages tweet storage and tracking"""

    def __init__(self, storage_dir: str = "data/tweets"):
        """
        Initialize tweet storage

        Args:
            storage_dir: Directory to store tweet data
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.storage_dir / "monitoring_state.json"

    def save_tweets(self, username: str, tweets: List[Dict[str, Any]]) -> None:
        """
        Save tweets to a JSON file

        Args:
            username: Twitter username
            tweets: List of tweet dictionaries
        """
        if not tweets:
            return

        filename = self.storage_dir / f"{username}_tweets.json"

        # Load existing tweets if file exists
        existing_tweets = []
        if filename.exists():
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    existing_tweets = data.get("tweets", [])
            except Exception as e:
                print(f"[WARN] Failed to load existing tweets: {e}")

        # Merge tweets (avoid duplicates)
        existing_ids = {tweet["id"] for tweet in existing_tweets}
        new_tweets = [t for t in tweets if t["id"] not in existing_ids]

        if new_tweets:
            all_tweets = new_tweets + existing_tweets
            all_tweets.sort(key=lambda x: x["created_at"], reverse=True)

            data = {
                "username": username,
                "last_updated": datetime.now().isoformat(),
                "total_tweets": len(all_tweets),
                "tweets": all_tweets
            }

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"[INFO] Saved {len(new_tweets)} new tweets for @{username}")

    def get_last_tweet_id(self, username: str) -> Optional[str]:
        """
        Get the ID of the last processed tweet for a user

        Args:
            username: Twitter username

        Returns:
            Last tweet ID or None
        """
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
                return state.get("users", {}).get(username, {}).get("last_tweet_id")
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"[WARN] Failed to read state file: {e}")
            return None

    def update_last_tweet_id(self, username: str, tweet_id: str, user_id: str) -> None:
        """
        Update the last processed tweet ID for a user

        Args:
            username: Twitter username
            tweet_id: Last processed tweet ID
            user_id: Twitter user ID
        """
        state = {"users": {}}

        # Load existing state
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
            except Exception as e:
                print(f"[WARN] Failed to load state file: {e}")

        # Update state
        if "users" not in state:
            state["users"] = {}

        state["users"][username] = {
            "user_id": user_id,
            "last_tweet_id": tweet_id,
            "last_updated": datetime.now().isoformat()
        }

        # Save state
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def get_monitored_users(self) -> Dict[str, Dict[str, str]]:
        """
        Get all monitored users

        Returns:
            Dictionary of monitored users with their state
        """
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
                return state.get("users", {})
        except FileNotFoundError:
            return {}
        except Exception as e:
            print(f"[WARN] Failed to read state file: {e}")
            return {}

    def get_all_tweets(self, username: str) -> List[Dict[str, Any]]:
        """
        Get all stored tweets for a user

        Args:
            username: Twitter username

        Returns:
            List of tweet dictionaries
        """
        filename = self.storage_dir / f"{username}_tweets.json"

        if not filename.exists():
            return []

        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("tweets", [])
        except Exception as e:
            print(f"[ERROR] Failed to load tweets: {e}")
            return []
