#!/usr/bin/env python3
"""
Agent 3: Daily Route & Reminder Agent

Purpose: Generate daily prioritized task lists and reminders for calls, visits, and reorders.

Trigger: Daily at 7 AM
Process:
1. Query Activities table for tasks due today
2. Query Orders table for reorders due this week
3. Generate prioritized task list
4. Send email/SMS to rep with daily plan

Usage:
    python3 agent3_daily_reminders.py --date 2024-12-03
    
Environment Variables Required:
    OPENAI_API_KEY - OpenAI API key
"""

import os
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from openai import OpenAI

class DailyReminderAgent:
    """Agent for generating daily task lists and reminders."""
    
    def __init__(self):
        """Initialize the agent with OpenAI client."""
        self.client = OpenAI()
    
    def get_tasks_due_today(self, activities_data: List[Dict]) -> List[Dict]:
        """
        Filter activities for tasks due today.
        
        Args:
            activities_data: List of activity records
            
        Returns:
            List of tasks due today
        """
        today = datetime.now().date()
        tasks_due = []
        
        for activity in activities_data:
            next_step_date = activity.get('next_step_date', '')
            if next_step_date:
                try:
                    task_date = datetime.strptime(next_step_date, '%Y-%m-%d').date()
                    if task_date <= today:
                        tasks_due.append(activity)
                except ValueError:
                    continue
        
        return tasks_due
    
    def get_reorders_due_soon(self, orders_data: List[Dict], days_ahead: int = 7) -> List[Dict]:
        """
        Filter orders for reorders due within specified days.
        
        Args:
            orders_data: List of order records
            days_ahead: Number of days to look ahead
            
        Returns:
            List of reorders due soon
        """
        today = datetime.now().date()
        future_date = today + timedelta(days=days_ahead)
        reorders_due = []
        
        for order in orders_data:
            next_reorder_date = order.get('next_reorder_date', '')
            if next_reorder_date:
                try:
                    reorder_date = datetime.strptime(next_reorder_date, '%Y-%m-%d').date()
                    if today <= reorder_date <= future_date:
                        reorders_due.append(order)
                except ValueError:
                    continue
        
        return reorders_due
    
    def prioritize_tasks(self, tasks: List[Dict], reorders: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Prioritize tasks using AI.
        
        Args:
            tasks: List of tasks due
            reorders: List of reorders due
            
        Returns:
            Dictionary with prioritized tasks by category
        """
        # Combine all items for prioritization
        all_items = []
        
        for task in tasks:
            all_items.append({
                "type": "task",
                "store": task.get('store_name', 'Unknown'),
                "action": task.get('next_step', 'Follow up'),
                "date": task.get('next_step_date', ''),
                "notes": task.get('ai_summary', ''),
                "priority_score": self._calculate_priority(task, is_reorder=False)
            })
        
        for reorder in reorders:
            all_items.append({
                "type": "reorder",
                "store": reorder.get('store_name', 'Unknown'),
                "brand": reorder.get('brand_name', 'Unknown'),
                "action": "Reorder check-in",
                "date": reorder.get('next_reorder_date', ''),
                "notes": f"Last order: {reorder.get('order_date', '')} - {reorder.get('cases', '')} cases",
                "priority_score": self._calculate_priority(reorder, is_reorder=True)
            })
        
        # Sort by priority score
        all_items.sort(key=lambda x: x['priority_score'], reverse=True)
        
        # Categorize
        prioritized = {
            "high_priority": [item for item in all_items if item['priority_score'] >= 8],
            "medium_priority": [item for item in all_items if 5 <= item['priority_score'] < 8],
            "low_priority": [item for item in all_items if item['priority_score'] < 5]
        }
        
        return prioritized
    
    def _calculate_priority(self, item: Dict, is_reorder: bool) -> int:
        """
        Calculate priority score for a task or reorder.
        
        Args:
            item: Task or reorder item
            is_reorder: Whether this is a reorder
            
        Returns:
            Priority score (1-10)
        """
        score = 5  # Base score
        
        if is_reorder:
            # Reorders are generally high priority
            score = 8
            
            # Check if overdue
            try:
                reorder_date = datetime.strptime(item.get('next_reorder_date', ''), '%Y-%m-%d').date()
                if reorder_date < datetime.now().date():
                    score = 10  # Overdue reorder is highest priority
            except:
                pass
        else:
            # Regular tasks
            next_step = item.get('next_step', '').lower()
            
            # Higher priority for certain actions
            if 'order' in next_step or 'close' in next_step:
                score = 9
            elif 'visit' in next_step or 'demo' in next_step:
                score = 7
            elif 'call' in next_step:
                score = 6
            elif 'email' in next_step:
                score = 4
            
            # Check if overdue
            try:
                task_date = datetime.strptime(item.get('next_step_date', ''), '%Y-%m-%d').date()
                days_overdue = (datetime.now().date() - task_date).days
                if days_overdue > 0:
                    score = min(10, score + days_overdue)  # Increase priority for overdue tasks
            except:
                pass
        
        return score
    
    def generate_daily_email(self, prioritized_tasks: Dict[str, List[Dict]], 
                           rep_name: str = "Sales Rep") -> str:
        """
        Generate a daily task email using AI.
        
        Args:
            prioritized_tasks: Dictionary with prioritized tasks
            rep_name: Name of the sales rep
            
        Returns:
            Email content
        """
        # Prepare task summary
        high_priority = prioritized_tasks.get('high_priority', [])
        medium_priority = prioritized_tasks.get('medium_priority', [])
        low_priority = prioritized_tasks.get('low_priority', [])
        
        total_tasks = len(high_priority) + len(medium_priority) + len(low_priority)
        
        # Format tasks for prompt
        tasks_text = "HIGH PRIORITY:\n"
        for i, task in enumerate(high_priority[:5], 1):  # Top 5
            tasks_text += f"{i}. {task['store']} - {task['action']} ({task['type']})\n"
            if task['notes']:
                tasks_text += f"   Notes: {task['notes'][:100]}\n"
        
        tasks_text += "\nMEDIUM PRIORITY:\n"
        for i, task in enumerate(medium_priority[:5], 1):  # Top 5
            tasks_text += f"{i}. {task['store']} - {task['action']} ({task['type']})\n"
        
        if len(low_priority) > 0:
            tasks_text += f"\nLOW PRIORITY: {len(low_priority)} additional tasks\n"
        
        prompt = f"""You are creating a daily task email for a field sales rep.

Rep Name: {rep_name}
Date: {datetime.now().strftime('%A, %B %d, %Y')}
Total Tasks: {total_tasks}

TASKS FOR TODAY:
{tasks_text}

Write a motivating and organized daily email that:
1. Greets the rep and sets a positive tone
2. Summarizes the day (e.g., "You have X high-priority tasks today")
3. Lists the top 5 high-priority tasks with clear action items
4. Mentions medium and low priority tasks briefly
5. Ends with an encouraging note
6. Keeps it concise (250-300 words)

Format:
Subject: [motivating subject line with date]

[email body]

Make it sound friendly and supportive, not robotic."""

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates motivating daily task emails for sales professionals."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_task_list_text(self, prioritized_tasks: Dict[str, List[Dict]]) -> str:
        """
        Generate a simple text task list.
        
        Args:
            prioritized_tasks: Dictionary with prioritized tasks
            
        Returns:
            Plain text task list
        """
        output = f"DAILY TASK LIST - {datetime.now().strftime('%Y-%m-%d')}\n"
        output += "=" * 50 + "\n\n"
        
        high_priority = prioritized_tasks.get('high_priority', [])
        medium_priority = prioritized_tasks.get('medium_priority', [])
        low_priority = prioritized_tasks.get('low_priority', [])
        
        if high_priority:
            output += "🔴 HIGH PRIORITY:\n"
            for i, task in enumerate(high_priority, 1):
                output += f"{i}. {task['store']} - {task['action']}\n"
                if task['notes']:
                    output += f"   📝 {task['notes'][:100]}\n"
                output += "\n"
        
        if medium_priority:
            output += "🟡 MEDIUM PRIORITY:\n"
            for i, task in enumerate(medium_priority, 1):
                output += f"{i}. {task['store']} - {task['action']}\n"
            output += "\n"
        
        if low_priority:
            output += f"🟢 LOW PRIORITY: {len(low_priority)} tasks\n"
        
        output += "\n" + "=" * 50 + "\n"
        output += f"Total tasks: {len(high_priority) + len(medium_priority) + len(low_priority)}\n"
        
        return output


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Generate daily task reminders")
    parser.add_argument("--rep-name", default="Sales Rep", help="Name of sales rep")
    parser.add_argument("--format", choices=["email", "text"], default="email",
                       help="Output format")
    
    args = parser.parse_args()
    
    # Sample data for testing
    sample_activities = [
        {
            "store_name": "ABC Liquor",
            "next_step": "Call to follow up",
            "next_step_date": datetime.now().strftime('%Y-%m-%d'),
            "ai_summary": "Interested in wellness products, asked about pricing"
        },
        {
            "store_name": "XYZ Smoke Shop",
            "next_step": "Visit with samples",
            "next_step_date": datetime.now().strftime('%Y-%m-%d'),
            "ai_summary": "Ready to try products, wants to see samples first"
        },
        {
            "store_name": "Corner Store",
            "next_step": "Send email with catalog",
            "next_step_date": (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            "ai_summary": "Requested product catalog and pricing"
        }
    ]
    
    sample_orders = [
        {
            "store_name": "Best Cafe",
            "brand_name": "Bodhi Bubbles",
            "order_date": (datetime.now() - timedelta(days=28)).strftime('%Y-%m-%d'),
            "next_reorder_date": (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
            "cases": "5"
        }
    ]
    
    # Initialize agent
    agent = DailyReminderAgent()
    
    # Get tasks
    tasks_due = agent.get_tasks_due_today(sample_activities)
    reorders_due = agent.get_reorders_due_soon(sample_orders)
    
    # Prioritize
    prioritized = agent.prioritize_tasks(tasks_due, reorders_due)
    
    # Generate output
    if args.format == "email":
        print(agent.generate_daily_email(prioritized, args.rep_name))
    else:
        print(agent.generate_task_list_text(prioritized))


if __name__ == "__main__":
    main()
