"""Seed the database with sample task data."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from src.database.task_db import TaskDatabase

def seed_tasks():
    """Create sample tasks for demonstration."""
    task_db = TaskDatabase()

    # Calculate dates
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)
    yesterday = today - timedelta(days=1)
    last_week = today - timedelta(days=7)

    sample_tasks = [
        # Pending tasks
        {
            "title": "Buy groceries",
            "description": "Get milk, eggs, bread, and vegetables from the supermarket",
            "due_date": tomorrow.strftime("%Y-%m-%d"),
            "priority": "high",
            "location": "New York",
            "status": "pending",
            "user_id": "alice"
        },
        {
            "title": "Prepare presentation",
            "description": "Create slides for Q4 business review meeting",
            "due_date": (today + timedelta(days=3)).strftime("%Y-%m-%d"),
            "priority": "high",
            "location": "San Francisco",
            "status": "in_progress",
            "user_id": "alice"
        },
        {
            "title": "Schedule dentist appointment",
            "description": "Book annual dental checkup",
            "due_date": next_week.strftime("%Y-%m-%d"),
            "priority": "medium",
            "location": "Boston",
            "status": "pending",
            "user_id": "bob"
        },
        {
            "title": "Review code submissions",
            "description": "Review pull requests from the development team",
            "due_date": today.strftime("%Y-%m-%d"),
            "priority": "high",
            "location": "Remote",
            "status": "in_progress",
            "user_id": "alice"
        },
        {
            "title": "Plan vacation itinerary",
            "description": "Research and plan activities for Tokyo trip",
            "due_date": (today + timedelta(days=14)).strftime("%Y-%m-%d"),
            "priority": "low",
            "location": "Tokyo",
            "status": "pending",
            "user_id": "bob"
        },
        {
            "title": "Update project documentation",
            "description": "Document new API endpoints and usage examples",
            "due_date": (today + timedelta(days=5)).strftime("%Y-%m-%d"),
            "priority": "medium",
            "location": "Remote",
            "status": "pending",
            "user_id": "alice"
        },
        {
            "title": "Team meeting preparation",
            "description": "Prepare agenda and materials for weekly team sync",
            "due_date": tomorrow.strftime("%Y-%m-%d"),
            "priority": "medium",
            "location": "London",
            "status": "in_progress",
            "user_id": "bob"
        },
        # Overdue tasks
        {
            "title": "Submit expense report",
            "description": "Submit Q3 business travel expenses",
            "due_date": yesterday.strftime("%Y-%m-%d"),
            "priority": "high",
            "location": "Paris",
            "status": "pending",
            "user_id": "alice"
        },
        {
            "title": "Renew software licenses",
            "description": "Renew annual licenses for development tools",
            "due_date": last_week.strftime("%Y-%m-%d"),
            "priority": "medium",
            "location": "Remote",
            "status": "pending",
            "user_id": "bob"
        },
        # Completed tasks
        {
            "title": "Complete project proposal",
            "description": "Write and submit proposal for new client project",
            "due_date": (today - timedelta(days=2)).strftime("%Y-%m-%d"),
            "priority": "high",
            "location": "Singapore",
            "status": "completed",
            "user_id": "alice"
        },
        {
            "title": "Attend training workshop",
            "description": "Cloud computing fundamentals workshop",
            "due_date": (today - timedelta(days=3)).strftime("%Y-%m-%d"),
            "priority": "medium",
            "location": "Seattle",
            "status": "completed",
            "user_id": "bob"
        },
        # Future tasks
        {
            "title": "Quarterly business review",
            "description": "Prepare and present quarterly performance metrics",
            "due_date": (today + timedelta(days=30)).strftime("%Y-%m-%d"),
            "priority": "high",
            "location": "Chicago",
            "status": "pending",
            "user_id": "alice"
        },
        {
            "title": "Server maintenance",
            "description": "Perform scheduled maintenance on production servers",
            "due_date": (today + timedelta(days=10)).strftime("%Y-%m-%d"),
            "priority": "high",
            "location": "Remote",
            "status": "pending",
            "user_id": "bob"
        },
        {
            "title": "Customer feedback analysis",
            "description": "Analyze customer survey results and create report",
            "due_date": (today + timedelta(days=6)).strftime("%Y-%m-%d"),
            "priority": "medium",
            "location": "Austin",
            "status": "pending",
            "user_id": "alice"
        },
        {
            "title": "Backup database",
            "description": "Create full backup of production database",
            "due_date": today.strftime("%Y-%m-%d"),
            "priority": "high",
            "location": "Remote",
            "status": "pending",
            "user_id": "bob"
        }
    ]

    print("Seeding tasks database...")
    created_count = 0

    for task_data in sample_tasks:
        try:
            task = task_db.create_task(**task_data)
            created_count += 1
            print(f"Created task: {task['title']} (ID: {task['id']})")
        except Exception as e:
            print(f"Failed to create task '{task_data['title']}': {e}")

    print(f"\n{created_count}/{len(sample_tasks)} tasks created successfully!")

    # Display statistics
    print("\n" + "="*60)
    print("Database Statistics:")
    print("="*60)

    stats = task_db.get_task_statistics()
    print(f"\nTotal tasks: {stats['total_tasks']}")

    print("\nBy Status:")
    for status, count in stats.get('by_status', {}).items():
        print(f"  - {status}: {count}")

    print("\nBy Priority:")
    for priority, count in stats.get('by_priority', {}).items():
        print(f"  - {priority}: {count}")

    print(f"\nOverdue tasks: {stats.get('overdue_count', 0)}")
    print(f"Due this week: {stats.get('due_this_week', 0)}")

    print("\n" + "="*60)
    print("Seed data created successfully!")
    print("="*60)


if __name__ == "__main__":
    seed_tasks()
