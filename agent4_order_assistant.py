#!/usr/bin/env python3
"""
Agent 4: Order Entry Assistant Agent

Purpose: Process order entries, calculate reorder dates, and create follow-up tasks.

Trigger: New order logged in Orders table
Process:
1. Calculate next reorder date (21-35 days)
2. Update store status to "customer"
3. Create reorder reminder task
4. Log activity in Activities table

Usage:
    python3 agent4_order_assistant.py --store-id ABC123 --brand-id XYZ789 --cases 5
    
Environment Variables Required:
    OPENAI_API_KEY - OpenAI API key
"""

import os
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from openai import OpenAI

class OrderAssistantAgent:
    """Agent for processing orders and managing reorder workflows."""
    
    # Reorder windows by product category (in days)
    REORDER_WINDOWS = {
        "beverages": (21, 28),
        "wellness": (28, 35),
        "tobacco": (21, 30),
        "food": (14, 21),
        "default": (21, 35)
    }
    
    def __init__(self):
        """Initialize the agent with OpenAI client."""
        self.client = OpenAI()
    
    def calculate_reorder_date(self, order_date: str, category: str = "default", 
                              cases_ordered: int = 1) -> str:
        """
        Calculate the optimal reorder date based on product category and order size.
        
        Args:
            order_date: Date of the order (YYYY-MM-DD)
            category: Product category
            cases_ordered: Number of cases ordered
            
        Returns:
            Recommended reorder date (YYYY-MM-DD)
        """
        # Get reorder window for category
        window = self.REORDER_WINDOWS.get(category.lower(), self.REORDER_WINDOWS["default"])
        min_days, max_days = window
        
        # Adjust based on order size
        # Larger orders = longer time to reorder
        if cases_ordered >= 10:
            days_until_reorder = max_days
        elif cases_ordered >= 5:
            days_until_reorder = (min_days + max_days) // 2
        else:
            days_until_reorder = min_days
        
        # Calculate reorder date
        order_dt = datetime.strptime(order_date, '%Y-%m-%d')
        reorder_dt = order_dt + timedelta(days=days_until_reorder)
        
        return reorder_dt.strftime('%Y-%m-%d')
    
    def generate_order_summary(self, order_info: Dict) -> str:
        """
        Generate a summary of the order using AI.
        
        Args:
            order_info: Dictionary with order details
            
        Returns:
            Order summary text
        """
        prompt = f"""You are summarizing a new order for a sales CRM.

ORDER DETAILS:
- Store: {order_info.get('store_name', 'Unknown')}
- Brand: {order_info.get('brand_name', 'Unknown')}
- Order Date: {order_info.get('order_date', '')}
- Cases: {order_info.get('cases', 0)}
- SKUs: {order_info.get('skus', 'N/A')}
- Order Type: {order_info.get('order_type', 'first')}
- Next Reorder Date: {order_info.get('next_reorder_date', '')}

Write a brief, professional summary (2-3 sentences) that:
1. Confirms the order details
2. Notes if this is a first order or reorder
3. Mentions the next reorder date
4. Sounds positive and appreciative

Keep it concise and professional."""

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates professional order summaries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=150
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_reorder_task(self, order_info: Dict) -> Dict[str, str]:
        """
        Generate a reorder reminder task.
        
        Args:
            order_info: Dictionary with order details
            
        Returns:
            Task details dictionary
        """
        task = {
            "subject": f"Reorder Check: {order_info.get('store_name', 'Store')} - {order_info.get('brand_name', 'Brand')}",
            "due_date": order_info.get('next_reorder_date', ''),
            "priority": "MEDIUM",
            "type": "TODO",
            "notes": f"""Time to check in on reorder for {order_info.get('store_name', 'this store')}.

Last Order Details:
- Date: {order_info.get('order_date', '')}
- Product: {order_info.get('brand_name', '')}
- Quantity: {order_info.get('cases', '')} cases
- SKUs: {order_info.get('skus', 'N/A')}

Action Items:
1. Call or visit the store
2. Ask how the products are selling
3. Check current inventory levels
4. Suggest reorder quantity
5. Address any concerns or feedback

Use the reorder email template in HubSpot notes."""
        }
        
        return task
    
    def generate_thank_you_note(self, order_info: Dict, is_first_order: bool = True) -> str:
        """
        Generate a thank you note for the order.
        
        Args:
            order_info: Dictionary with order details
            is_first_order: Whether this is the store's first order
            
        Returns:
            Thank you note text
        """
        prompt = f"""You are writing a thank you note for a sales rep to send after receiving an order.

ORDER DETAILS:
- Store: {order_info.get('store_name', 'Unknown')}
- Brand: {order_info.get('brand_name', 'Unknown')}
- Cases: {order_info.get('cases', 0)}
- First Order: {'Yes' if is_first_order else 'No'}

Write a brief thank you note (3-4 sentences) that:
1. Thanks them for the order
2. {'Welcomes them as a new partner' if is_first_order else 'Appreciates their continued business'}
3. Offers support and mentions you'll check in soon
4. Sounds genuine and personal, not generic

Format as an email or text message.

Subject: [subject line]

[message body]

Best regards,
[Your Name]"""

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are an expert at writing genuine, personalized thank you notes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=250
        )
        
        return response.choices[0].message.content.strip()
    
    def create_activity_log(self, order_info: Dict) -> Dict[str, str]:
        """
        Create an activity log entry for the order.
        
        Args:
            order_info: Dictionary with order details
            
        Returns:
            Activity log entry
        """
        return {
            "store_id": order_info.get('store_id', ''),
            "activity_type": "order",
            "date": order_info.get('order_date', ''),
            "raw_notes": f"Order placed: {order_info.get('brand_name', '')} - {order_info.get('cases', '')} cases",
            "ai_summary": self.generate_order_summary(order_info),
            "outcome": "ordered",
            "next_step": "Check in for reorder",
            "next_step_date": order_info.get('next_reorder_date', '')
        }
    
    def process_order(self, order_info: Dict) -> Dict[str, any]:
        """
        Process a complete order workflow.
        
        Args:
            order_info: Dictionary with order details
            
        Returns:
            Dictionary with all generated outputs
        """
        # Determine if first order
        is_first_order = order_info.get('order_type', 'first').lower() == 'first'
        
        # Calculate reorder date if not provided
        if not order_info.get('next_reorder_date'):
            order_info['next_reorder_date'] = self.calculate_reorder_date(
                order_info.get('order_date', datetime.now().strftime('%Y-%m-%d')),
                order_info.get('category', 'default'),
                int(order_info.get('cases', 1))
            )
        
        # Generate all outputs
        result = {
            "order_summary": self.generate_order_summary(order_info),
            "reorder_task": self.generate_reorder_task(order_info),
            "thank_you_note": self.generate_thank_you_note(order_info, is_first_order),
            "activity_log": self.create_activity_log(order_info),
            "next_reorder_date": order_info['next_reorder_date'],
            "new_store_status": "customer" if is_first_order else "active_customer"
        }
        
        return result


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Process order and generate follow-up tasks")
    parser.add_argument("--store-name", required=True, help="Store name")
    parser.add_argument("--brand-name", required=True, help="Brand name")
    parser.add_argument("--order-date", default=datetime.now().strftime('%Y-%m-%d'),
                       help="Order date (YYYY-MM-DD)")
    parser.add_argument("--cases", type=int, default=1, help="Number of cases")
    parser.add_argument("--skus", default="", help="SKUs ordered")
    parser.add_argument("--order-type", choices=["first", "reorder"], default="first",
                       help="Type of order")
    parser.add_argument("--category", default="default", help="Product category")
    
    args = parser.parse_args()
    
    # Build order info
    order_info = {
        "store_name": args.store_name,
        "brand_name": args.brand_name,
        "order_date": args.order_date,
        "cases": args.cases,
        "skus": args.skus,
        "order_type": args.order_type,
        "category": args.category
    }
    
    # Initialize agent
    agent = OrderAssistantAgent()
    
    # Process order
    print(f"Processing order for {args.store_name}...\n")
    result = agent.process_order(order_info)
    
    # Display results
    print("=" * 60)
    print("ORDER SUMMARY")
    print("=" * 60)
    print(result['order_summary'])
    
    print("\n" + "=" * 60)
    print("THANK YOU NOTE")
    print("=" * 60)
    print(result['thank_you_note'])
    
    print("\n" + "=" * 60)
    print("REORDER TASK")
    print("=" * 60)
    print(f"Subject: {result['reorder_task']['subject']}")
    print(f"Due Date: {result['reorder_task']['due_date']}")
    print(f"Priority: {result['reorder_task']['priority']}")
    print(f"\nNotes:\n{result['reorder_task']['notes']}")
    
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print(f"Next Reorder Date: {result['next_reorder_date']}")
    print(f"Store Status: {result['new_store_status']}")


if __name__ == "__main__":
    main()
