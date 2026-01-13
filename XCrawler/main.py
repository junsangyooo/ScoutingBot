"""
X Tweet Monitor - Main Entry Point
Real-time monitoring of Twitter/X user posts
"""
from tweet_monitor import TweetMonitor
from config import XAPIConfig
from typing import List, Dict


def on_new_tweets(username: str, tweets: List[Dict]) -> None:
    """
    Callback function when new tweets are detected

    Args:
        username: Twitter username
        tweets: List of new tweet dictionaries
    """
    print(f"\n{'='*60}")
    print(f"🆕 NEW TWEETS from @{username}")
    print(f"{'='*60}")

    for tweet in tweets:
        print(f"\n📝 Tweet ID: {tweet['id']}")
        print(f"🕒 Created: {tweet['created_at']}")
        print(f"📄 Text: {tweet['text']}")
        print(f"🔗 URL: {tweet['url']}")

        metrics = tweet.get('metrics', {})
        if metrics:
            print(f"📊 Metrics: "
                  f"❤️ {metrics.get('like_count', 0)} | "
                  f"🔄 {metrics.get('retweet_count', 0)} | "
                  f"💬 {metrics.get('reply_count', 0)}")

    print(f"\n{'='*60}\n")


def main():
    """Main function"""
    print("=" * 60)
    print("X Tweet Monitor - Real-time Tweet Tracking")
    print("=" * 60)

    # Validate configuration
    try:
        XAPIConfig.validate()
    except ValueError as e:
        print(f"\n[ERROR] Configuration error: {e}")
        print("\nPlease create a .env file with your X API credentials.")
        print("See .env.example for reference.")
        return

    # Initialize monitor
    monitor = TweetMonitor(
        storage_dir="../data/tweets"  # Store in project root data folder
    )

    # Add callback for new tweets
    monitor.add_callback(on_new_tweets)

    # Example: Monitor specific users
    # You can add multiple users to monitor
    print("\n📋 Add users to monitor:")
    print("Example: elonmusk, OpenAI, AnthropicAI, etc.\n")

    # You can modify this list or make it interactive
    users_to_monitor = [
        "elonmusk",        # Elon Musk
        # "OpenAI",        # OpenAI
        # "AnthropicAI",   # Anthropic
        # Add more users here
    ]

    # Or make it interactive
    print("Enter Twitter usernames to monitor (comma-separated):")
    print("Or press Enter to use default list:")
    user_input = input("> ").strip()

    if user_input:
        users_to_monitor = [u.strip().replace("@", "") for u in user_input.split(",")]

    # Add users to monitor
    success_count = 0
    for username in users_to_monitor:
        if monitor.add_user(
            username=username,
            exclude_replies=True,   # Don't monitor replies
            exclude_retweets=True   # Don't monitor retweets
        ):
            success_count += 1

    if success_count == 0:
        print("\n[ERROR] No users were successfully added to monitoring")
        return

    print(f"\n✅ Successfully added {success_count} users to monitoring\n")

    # Start continuous monitoring
    try:
        monitor.start()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")


if __name__ == "__main__":
    main()
