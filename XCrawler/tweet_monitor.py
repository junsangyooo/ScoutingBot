"""
Tweet Monitor Service
Real-time monitoring service for Twitter/X user posts
"""
import time
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from x_client import XAPIClient
from tweet_storage import TweetStorage
from config import XAPIConfig


class TweetMonitor:
    """Monitor Twitter/X users for new tweets"""

    def __init__(
        self,
        bearer_token: Optional[str] = None,
        storage_dir: str = "data/tweets",
        poll_interval: Optional[int] = None
    ):
        """
        Initialize tweet monitor

        Args:
            bearer_token: X API bearer token
            storage_dir: Directory to store tweet data
            poll_interval: Polling interval in seconds
        """
        self.client = XAPIClient(bearer_token)
        self.storage = TweetStorage(storage_dir)
        self.poll_interval = poll_interval or XAPIConfig.POLL_INTERVAL_SECONDS
        self.monitored_users: Dict[str, Dict[str, str]] = {}
        self.is_running = False
        self.callbacks: List[Callable[[str, List[Dict]], None]] = []

    def add_user(self, username: str, exclude_replies: bool = True, exclude_retweets: bool = True) -> bool:
        """
        Add a user to monitor

        Args:
            username: Twitter username (without @)
            exclude_replies: Whether to exclude replies
            exclude_retweets: Whether to exclude retweets

        Returns:
            True if user was added successfully
        """
        print(f"[INFO] Adding user to monitor: @{username}")

        # Get user ID
        user_id = self.client.get_user_id_by_username(username)
        if not user_id:
            print(f"[ERROR] Failed to get user ID for @{username}")
            return False

        # Check for existing tweets
        last_tweet_id = self.storage.get_last_tweet_id(username)

        if not last_tweet_id:
            # First time monitoring - fetch latest tweets
            print(f"[INFO] First time monitoring @{username}, fetching latest tweets...")
            tweets = self.client.get_latest_tweets(
                username=username,
                max_results=10,
                exclude_replies=exclude_replies,
                exclude_retweets=exclude_retweets
            )

            if tweets:
                formatted_tweets = [self.client.format_tweet(t) for t in tweets]
                self.storage.save_tweets(username, formatted_tweets)
                last_tweet_id = tweets[0]["id"]
                self.storage.update_last_tweet_id(username, last_tweet_id, user_id)
                print(f"[INFO] Initialized with {len(tweets)} latest tweets")

        # Add to monitored users
        self.monitored_users[username] = {
            "user_id": user_id,
            "last_tweet_id": last_tweet_id or "",
            "exclude_replies": exclude_replies,
            "exclude_retweets": exclude_retweets
        }

        print(f"[INFO] Successfully added @{username} to monitoring")
        return True

    def remove_user(self, username: str) -> None:
        """
        Remove a user from monitoring

        Args:
            username: Twitter username (without @)
        """
        if username in self.monitored_users:
            del self.monitored_users[username]
            print(f"[INFO] Removed @{username} from monitoring")

    def add_callback(self, callback: Callable[[str, List[Dict]], None]) -> None:
        """
        Add a callback function to be called when new tweets are found

        Args:
            callback: Function that takes (username, new_tweets) as arguments
        """
        self.callbacks.append(callback)

    def check_for_new_tweets(self, username: str) -> List[Dict[str, Any]]:
        """
        Check for new tweets from a specific user

        Args:
            username: Twitter username (without @)

        Returns:
            List of new tweets
        """
        user_info = self.monitored_users.get(username)
        if not user_info:
            return []

        user_id = user_info["user_id"]
        last_tweet_id = user_info["last_tweet_id"]

        if not last_tweet_id:
            return []

        # Fetch new tweets
        new_tweets = self.client.get_new_tweets_since(
            user_id=user_id,
            since_id=last_tweet_id,
            exclude_replies=user_info.get("exclude_replies", True),
            exclude_retweets=user_info.get("exclude_retweets", True)
        )

        if new_tweets:
            # Format and save
            formatted_tweets = [self.client.format_tweet(t) for t in new_tweets]
            self.storage.save_tweets(username, formatted_tweets)

            # Update last tweet ID
            latest_id = new_tweets[0]["id"]
            self.storage.update_last_tweet_id(username, latest_id, user_id)
            self.monitored_users[username]["last_tweet_id"] = latest_id

            print(f"[INFO] Found {len(new_tweets)} new tweets from @{username}")

            # Call callbacks
            for callback in self.callbacks:
                try:
                    callback(username, formatted_tweets)
                except Exception as e:
                    print(f"[ERROR] Callback error: {e}")

            return formatted_tweets

        return []

    def run_once(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Check all monitored users once

        Returns:
            Dictionary of username -> new_tweets
        """
        results = {}

        for username in list(self.monitored_users.keys()):
            try:
                new_tweets = self.check_for_new_tweets(username)
                if new_tweets:
                    results[username] = new_tweets
            except Exception as e:
                print(f"[ERROR] Failed to check @{username}: {e}")

        return results

    def start(self) -> None:
        """
        Start continuous monitoring

        This will run indefinitely until stop() is called
        """
        if not self.monitored_users:
            print("[WARN] No users to monitor. Add users first with add_user()")
            return

        self.is_running = True
        print(f"[INFO] Starting tweet monitor for {len(self.monitored_users)} users")
        print(f"[INFO] Polling interval: {self.poll_interval} seconds")
        print(f"[INFO] Monitoring: {', '.join('@' + u for u in self.monitored_users.keys())}")
        print("[INFO] Press Ctrl+C to stop\n")

        try:
            while self.is_running:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] Checking for new tweets...")

                new_tweets_found = self.run_once()

                if new_tweets_found:
                    for username, tweets in new_tweets_found.items():
                        print(f"  [@{username}] {len(tweets)} new tweets")
                else:
                    print("  No new tweets")

                # Wait for next poll
                time.sleep(self.poll_interval)

        except KeyboardInterrupt:
            print("\n[INFO] Stopping tweet monitor...")
            self.stop()

    def stop(self) -> None:
        """Stop the monitoring service"""
        self.is_running = False
        print("[INFO] Tweet monitor stopped")

    def load_monitored_users(self) -> None:
        """Load previously monitored users from storage"""
        users = self.storage.get_monitored_users()

        for username, info in users.items():
            self.monitored_users[username] = {
                "user_id": info["user_id"],
                "last_tweet_id": info["last_tweet_id"],
                "exclude_replies": True,
                "exclude_retweets": True
            }

        if users:
            print(f"[INFO] Loaded {len(users)} previously monitored users")
