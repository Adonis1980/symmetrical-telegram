#!/usr/bin/env python3
"""
Agent 5: Weekly Report Generator Agent

Purpose: Generate comprehensive weekly sales reports with metrics and insights.

Trigger: Weekly on Monday at 9 AM
Process:
1. Pull data from past week: new stores, orders, activities
2. Calculate metrics: conversion rate, orders by brand, reorders
3. Generate formatted report
4. Email to rep

Usage:
    python3 agent5_weekly_reports.py --start-date 2024-11-25 --end-date 2024-12-01
    
Environment Variables Required:
    OPENAI_API_KEY - OpenAI API key
"""

import os
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from openai import OpenAI

class WeeklyReportAgent:
    """Agent for generating weekly sales reports."""
    
    def __init__(self):
        """Initialize the agent with OpenAI client."""
        self.client = OpenAI()
    
    def calculate_metrics(self, stores_data: List[Dict], orders_data: List[Dict], 
                         activities_data: List[Dict]) -> Dict:
        """
        Calculate key sales metrics for the week.
        
        Args:
            stores_data: List of store records
            orders_data: List of order records
            activities_data: List of activity records
            
        Returns:
            Dictionary with calculated metrics
        """
        metrics = {
            "new_stores_added": 0,
            "total_stores": len(stores_data),
            "total_orders": len(orders_data),
            "first_orders": 0,
            "reorders": 0,
            "total_cases": 0,
            "orders_by_brand": {},
            "total_activities": len(activities_data),
            "calls_made": 0,
            "visits_made": 0,
            "emails_sent": 0,
            "conversion_rate": 0.0,
            "stores_contacted": 0,
            "stores_converted": 0
        }
        
        # Process stores
        for store in stores_data:
            if store.get('status') == 'new':
                metrics['new_stores_added'] += 1
        
        # Process orders
        for order in orders_data:
            if order.get('order_type') == 'first':
                metrics['first_orders'] += 1
            else:
                metrics['reorders'] += 1
            
            cases = int(order.get('cases', 0))
            metrics['total_cases'] += cases
            
            brand = order.get('brand_name', 'Unknown')
            if brand in metrics['orders_by_brand']:
                metrics['orders_by_brand'][brand] += 1
            else:
                metrics['orders_by_brand'][brand] = 1
        
        # Process activities
        contacted_stores = set()
        converted_stores = set()
        
        for activity in activities_data:
            activity_type = activity.get('activity_type', '').lower()
            
            if activity_type == 'call':
                metrics['calls_made'] += 1
            elif activity_type == 'visit':
                metrics['visits_made'] += 1
            elif activity_type == 'email':
                metrics['emails_sent'] += 1
            
            store_id = activity.get('store_id')
            if store_id:
                contacted_stores.add(store_id)
                
                if activity.get('outcome') == 'ordered':
                    converted_stores.add(store_id)
        
        metrics['stores_contacted'] = len(contacted_stores)
        metrics['stores_converted'] = len(converted_stores)
        
        # Calculate conversion rate
        if metrics['stores_contacted'] > 0:
            metrics['conversion_rate'] = (metrics['stores_converted'] / metrics['stores_contacted']) * 100
        
        return metrics
    
    def generate_insights(self, metrics: Dict) -> List[str]:
        """
        Generate AI-powered insights from metrics.
        
        Args:
            metrics: Dictionary with calculated metrics
            
        Returns:
            List of insight strings
        """
        prompt = f"""You are analyzing weekly sales performance data for a field sales rep.

METRICS:
- New Stores Added: {metrics['new_stores_added']}
- Total Orders: {metrics['total_orders']}
- First Orders: {metrics['first_orders']}
- Reorders: {metrics['reorders']}
- Total Cases Sold: {metrics['total_cases']}
- Calls Made: {metrics['calls_made']}
- Visits Made: {metrics['visits_made']}
- Emails Sent: {metrics['emails_sent']}
- Conversion Rate: {metrics['conversion_rate']:.1f}%
- Stores Contacted: {metrics['stores_contacted']}
- Stores Converted: {metrics['stores_converted']}

Top Brands by Orders:
{json.dumps(metrics['orders_by_brand'], indent=2)}

Generate 3-5 actionable insights and recommendations based on this data. Each insight should:
1. Highlight a trend or pattern
2. Explain what it means
3. Suggest a specific action to take

Format as a numbered list. Be specific and actionable, not generic."""

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a sales analytics expert who provides actionable insights from data."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        insights_text = response.choices[0].message.content.strip()
        
        # Split into list
        insights = [line.strip() for line in insights_text.split('\n') if line.strip() and line.strip()[0].isdigit()]
        
        return insights
    
    def generate_weekly_report(self, metrics: Dict, insights: List[str], 
                              start_date: str, end_date: str,
                              rep_name: str = "Sales Rep") -> str:
        """
        Generate a formatted weekly report.
        
        Args:
            metrics: Dictionary with calculated metrics
            insights: List of insights
            start_date: Start date of reporting period
            end_date: End date of reporting period
            rep_name: Name of sales rep
            
        Returns:
            Formatted report text
        """
        prompt = f"""You are creating a weekly sales report for a field sales rep.

REPORTING PERIOD: {start_date} to {end_date}
REP NAME: {rep_name}

KEY METRICS:
- New Stores Added: {metrics['new_stores_added']}
- Total Active Stores: {metrics['total_stores']}
- Total Orders This Week: {metrics['total_orders']}
  - First Orders: {metrics['first_orders']}
  - Reorders: {metrics['reorders']}
- Total Cases Sold: {metrics['total_cases']}
- Conversion Rate: {metrics['conversion_rate']:.1f}%

ACTIVITY SUMMARY:
- Calls Made: {metrics['calls_made']}
- Visits Made: {metrics['visits_made']}
- Emails Sent: {metrics['emails_sent']}
- Stores Contacted: {metrics['stores_contacted']}
- Stores Converted: {metrics['stores_converted']}

TOP BRANDS:
{json.dumps(metrics['orders_by_brand'], indent=2)}

AI INSIGHTS:
{chr(10).join(insights)}

Write a professional weekly sales report email that:
1. Opens with a positive, motivating greeting
2. Summarizes the week's performance highlights
3. Presents key metrics in an organized way
4. Includes the AI insights
5. Recognizes achievements and progress
6. Suggests focus areas for next week
7. Ends with encouragement
8. Keeps it concise but comprehensive (400-500 words)

Format:
Subject: [motivating subject line with week dates]

[email body with clear sections]

Use professional but friendly tone. Include some emoji for visual interest but don't overdo it."""

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are an expert at creating motivating, data-driven sales reports."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_markdown_report(self, metrics: Dict, insights: List[str],
                                start_date: str, end_date: str,
                                rep_name: str = "Sales Rep") -> str:
        """
        Generate a markdown-formatted report for documentation.
        
        Args:
            metrics: Dictionary with calculated metrics
            insights: List of insights
            start_date: Start date of reporting period
            end_date: End date of reporting period
            rep_name: Name of sales rep
            
        Returns:
            Markdown formatted report
        """
        report = f"""# Weekly Sales Report

**Rep:** {rep_name}  
**Period:** {start_date} to {end_date}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## Executive Summary

This week, you added **{metrics['new_stores_added']} new stores**, closed **{metrics['total_orders']} orders** ({metrics['first_orders']} first-time, {metrics['reorders']} reorders), and sold **{metrics['total_cases']} cases** across all brands. Your conversion rate was **{metrics['conversion_rate']:.1f}%**.

---

## Key Metrics

### Sales Performance

| Metric | Value |
|--------|-------|
| Total Orders | {metrics['total_orders']} |
| First Orders | {metrics['first_orders']} |
| Reorders | {metrics['reorders']} |
| Total Cases Sold | {metrics['total_cases']} |
| Conversion Rate | {metrics['conversion_rate']:.1f}% |

### Store Pipeline

| Metric | Value |
|--------|-------|
| New Stores Added | {metrics['new_stores_added']} |
| Total Active Stores | {metrics['total_stores']} |
| Stores Contacted | {metrics['stores_contacted']} |
| Stores Converted | {metrics['stores_converted']} |

### Activity Summary

| Activity Type | Count |
|---------------|-------|
| Calls Made | {metrics['calls_made']} |
| Visits Made | {metrics['visits_made']} |
| Emails Sent | {metrics['emails_sent']} |
| Total Activities | {metrics['total_activities']} |

---

## Orders by Brand

"""
        
        # Add brand breakdown
        if metrics['orders_by_brand']:
            report += "| Brand | Orders |\n|-------|--------|\n"
            for brand, count in sorted(metrics['orders_by_brand'].items(), key=lambda x: x[1], reverse=True):
                report += f"| {brand} | {count} |\n"
        else:
            report += "*No orders this week*\n"
        
        report += "\n---\n\n## AI-Generated Insights\n\n"
        
        # Add insights
        for insight in insights:
            report += f"{insight}\n\n"
        
        report += "---\n\n## Next Week Focus\n\n"
        report += "Based on this week's performance, prioritize:\n\n"
        
        # Generate focus areas based on metrics
        if metrics['reorders'] < metrics['first_orders']:
            report += "- **Reorder Follow-ups**: You have more first orders than reorders. Focus on checking in with recent customers.\n"
        
        if metrics['conversion_rate'] < 20:
            report += "- **Qualification**: Conversion rate is low. Spend more time qualifying leads before outreach.\n"
        
        if metrics['visits_made'] < 5:
            report += "- **In-Person Visits**: Increase face-to-face meetings to build stronger relationships.\n"
        
        report += "\n---\n\n*Report generated automatically by Agent 5: Weekly Report Generator*\n"
        
        return report
    
    def create_charts_data(self, metrics: Dict) -> Dict:
        """
        Create data structures for charts/visualizations.
        
        Args:
            metrics: Dictionary with calculated metrics
            
        Returns:
            Dictionary with chart data
        """
        return {
            "orders_chart": {
                "labels": ["First Orders", "Reorders"],
                "data": [metrics['first_orders'], metrics['reorders']]
            },
            "activity_chart": {
                "labels": ["Calls", "Visits", "Emails"],
                "data": [metrics['calls_made'], metrics['visits_made'], metrics['emails_sent']]
            },
            "brands_chart": {
                "labels": list(metrics['orders_by_brand'].keys()),
                "data": list(metrics['orders_by_brand'].values())
            },
            "conversion_funnel": {
                "labels": ["Contacted", "Converted"],
                "data": [metrics['stores_contacted'], metrics['stores_converted']]
            }
        }


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Generate weekly sales report")
    parser.add_argument("--start-date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="End date (YYYY-MM-DD)")
    parser.add_argument("--rep-name", default="Sales Rep", help="Name of sales rep")
    parser.add_argument("--format", choices=["email", "markdown", "json"], default="email",
                       help="Output format")
    
    args = parser.parse_args()
    
    # Default to last week if no dates provided
    if not args.start_date or not args.end_date:
        today = datetime.now()
        end_date = today - timedelta(days=today.weekday() + 1)  # Last Sunday
        start_date = end_date - timedelta(days=6)  # Previous Monday
        args.start_date = start_date.strftime('%Y-%m-%d')
        args.end_date = end_date.strftime('%Y-%m-%d')
    
    # Sample data for testing
    sample_stores = [
        {"store_id": "1", "status": "new"},
        {"store_id": "2", "status": "customer"},
        {"store_id": "3", "status": "customer"}
    ]
    
    sample_orders = [
        {"order_type": "first", "cases": "5", "brand_name": "Bodhi Bubbles"},
        {"order_type": "first", "cases": "3", "brand_name": "Kush Kube"},
        {"order_type": "reorder", "cases": "10", "brand_name": "Bodhi Bubbles"}
    ]
    
    sample_activities = [
        {"activity_type": "call", "store_id": "1", "outcome": "interested"},
        {"activity_type": "visit", "store_id": "2", "outcome": "ordered"},
        {"activity_type": "email", "store_id": "3", "outcome": "no_response"},
        {"activity_type": "call", "store_id": "2", "outcome": "ordered"}
    ]
    
    # Initialize agent
    agent = WeeklyReportAgent()
    
    # Calculate metrics
    print(f"Generating report for {args.start_date} to {args.end_date}...\n")
    metrics = agent.calculate_metrics(sample_stores, sample_orders, sample_activities)
    
    # Generate insights
    insights = agent.generate_insights(metrics)
    
    # Generate output based on format
    if args.format == "email":
        report = agent.generate_weekly_report(metrics, insights, args.start_date, args.end_date, args.rep_name)
        print(report)
    
    elif args.format == "markdown":
        report = agent.generate_markdown_report(metrics, insights, args.start_date, args.end_date, args.rep_name)
        print(report)
    
    elif args.format == "json":
        output = {
            "period": {
                "start": args.start_date,
                "end": args.end_date
            },
            "metrics": metrics,
            "insights": insights,
            "charts": agent.create_charts_data(metrics)
        }
        print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
