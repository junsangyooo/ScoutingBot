#!/usr/bin/env python3
"""
Daily Company Crawler with Slack Notification
Automatically runs the crawler and sends formatted results to Slack
"""

import sys
import json
import os
from datetime import datetime
from io import StringIO
import requests

# Add company_crawler to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'company_crawler'))

from physical_intelligence.main import run as run_pi
from skild_ai.main import run as run_skild
from dyna.main import run as run_dyna

COMPANIES = {
    "pi": ("Physical Intelligence", run_pi),
    "skild": ("Skild AI", run_skild),
    "dyna": ("DYNA", run_dyna),
}


def crawl_all_companies(purpose="all"):
    """Run crawler for all companies"""
    results = []

    for key, (name, runner) in COMPANIES.items():
        print(f"\n[INFO] Crawling {name}...")
        try:
            result = runner(purpose)
            results.append(result)
            print(f"[INFO] {name} completed")
        except Exception as e:
            print(f"[ERROR] {name} failed: {e}")
            results.append({"company": name, "error": str(e)})

    return results


def format_slack_message(results):
    """Format crawling results for Slack with detailed status for all 7 sections"""

    # Slack Block Kit format
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🤖 Daily Company Crawler Report",
                "emoji": True
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"*Date:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')}"
                }
            ]
        },
        {
            "type": "divider"
        }
    ]

    has_updates = False

    for result in results:
        if not result:
            continue

        company = result.get("company", "Unknown")
        company_text = f"*{company}*\n"

        if "error" in result:
            company_text += f"❌ *Error:* {result['error']}\n"
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": company_text
                }
            })
            blocks.append({"type": "divider"})
            continue

        # Team updates (PI only)
        team_data = result.get("team", {})
        if team_data:
            status = team_data.get("status", "initialized")
            if status == "updated":
                has_updates = True
                added = team_data.get("added", [])
                removed = team_data.get("removed", [])

                company_text += "- *Team:*\n"
                if added:
                    company_text += "  - *Added:*\n"
                    for member in added:
                        name = member.get('name', 'Unknown')
                        company_text += f"    • {name}\n"
                if removed:
                    company_text += "  - *Removed:*\n"
                    for member in removed:
                        name = member.get('name', 'Unknown')
                        company_text += f"    • {name}\n"
            else:
                company_text += "- *Team:* Checked\n"

        # Blog/Research updates
        blog_data = result.get("blog") or result.get("research", {})
        if blog_data:
            status = blog_data.get("status", "initialized")
            if status == "updated":
                has_updates = True
                added = blog_data.get("added", [])
                removed = blog_data.get("removed", [])
                updated = blog_data.get("updated", [])

                company_text += "- *Blog:*\n"
                if added:
                    company_text += "  - *Added:*\n"
                    for post in added:
                        title = post.get('title', 'Untitled')
                        url = post.get('url', '')
                        if url:
                            company_text += f"    • <{url}|{title}>\n"
                        else:
                            company_text += f"    • {title}\n"
                if removed:
                    company_text += "  - *Removed:*\n"
                    for post in removed:
                        title = post.get('title', 'Untitled')
                        url = post.get('url', '')
                        if url:
                            company_text += f"    • <{url}|{title}>\n"
                        else:
                            company_text += f"    • {title}\n"
                if updated:
                    company_text += "  - *Updated:*\n"
                    for post in updated:
                        title = post.get('title', 'Untitled')
                        url = post.get('url', '')
                        if url:
                            company_text += f"    • <{url}|{title}>\n"
                        else:
                            company_text += f"    • {title}\n"
            else:
                company_text += "- *Blog:* Checked\n"

        # Position updates
        pos_data = result.get("position", {})
        if pos_data:
            status = pos_data.get("status", "initialized")
            if status == "updated":
                has_updates = True
                added = pos_data.get("added", [])
                removed = pos_data.get("removed", [])
                updated = pos_data.get("updated", [])

                company_text += "- *Career:*\n"
                if added:
                    company_text += "  - *Added:*\n"
                    for pos in added:
                        title = pos.get('title', 'Untitled')
                        url = pos.get('url', '')
                        if url:
                            company_text += f"    • <{url}|{title}>\n"
                        else:
                            company_text += f"    • {title}\n"
                if removed:
                    company_text += "  - *Removed:*\n"
                    for pos in removed:
                        title = pos.get('title', 'Untitled')
                        url = pos.get('url', '')
                        if url:
                            company_text += f"    • <{url}|{title}>\n"
                        else:
                            company_text += f"    • {title}\n"
                if updated:
                    company_text += "  - *Updated:*\n"
                    for pos in updated:
                        title = pos.get('title', 'Untitled')
                        url = pos.get('url', '')
                        if url:
                            company_text += f"    • <{url}|{title}>\n"
                        else:
                            company_text += f"    • {title}\n"
            else:
                company_text += "- *Career:* Checked\n"

        # Add company section
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": company_text
            }
        })

        # Add blank line (divider) after each company
        blocks.append({"type": "divider"})

    # Summary
    if not has_updates:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "✅ *Summary:* No significant changes detected"
            }
        })
    else:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "🔔 *Summary:* Updates detected! Check details above."
            }
        })

    return {"blocks": blocks}


def send_slack_notification(webhook_url, results):
    """Send formatted results to Slack"""

    try:
        message = format_slack_message(results)

        response = requests.post(
            webhook_url,
            json=message,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            print("\n✅ Slack notification sent successfully!")
            return True
        else:
            print(f"\n❌ Failed to send Slack notification: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"\n❌ Error sending Slack notification: {e}")
        return False


def main():
    """Main execution function"""

    # Get Slack webhook URL from environment variable
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')

    # Check if running in test mode
    test_mode = os.environ.get('TEST_MODE', '').lower() in ['true', '1', 'yes']

    if not webhook_url and not test_mode:
        print("❌ ERROR: SLACK_WEBHOOK_URL environment variable not set")
        print("Please set it in ~/.bashrc or the cron script")
        print("\nOr run in test mode:")
        print("  TEST_MODE=true python3 daily_crawler.py")
        sys.exit(1)

    print("=" * 60)
    print(f"🚀 Starting Daily Company Crawler")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')}")
    print("=" * 60)

    # Run crawler
    results = crawl_all_companies(purpose="all")

    # Print results to console
    print("\n" + "=" * 60)
    print("📊 CRAWL RESULTS")
    print("=" * 60)

    for result in results:
        if result:
            company = result.get("company", "Unknown")
            print(f"\n[{company}]")
            if "error" in result:
                print(f"  ❌ Error: {result['error']}")
            else:
                print(f"  ✅ Success")

    # Send Slack notification
    if webhook_url:
        print("\n" + "=" * 60)
        print("📤 Sending Slack Notification...")
        print("=" * 60)

        send_slack_notification(webhook_url, results)
    elif test_mode:
        print("\n" + "=" * 60)
        print("⚠️  TEST MODE: Skipping Slack notification")
        print("=" * 60)

    print("\n✅ Daily crawler completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
