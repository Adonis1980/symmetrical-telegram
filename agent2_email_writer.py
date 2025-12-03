#!/usr/bin/env python3
"""
Agent 2: Email & Follow-up Writer Agent

Purpose: Generate personalized outreach emails, text scripts, and call scripts.

Trigger: New qualified store OR new brand launch
Process:
1. Read store record + brand profile
2. Generate intro email, text/DM script, call script
3. Save to HubSpot as notes
4. Create task for rep to review and send

Usage:
    python3 agent2_email_writer.py --store-id ABC123 --brand-id XYZ789 --stage new
    
Environment Variables Required:
    OPENAI_API_KEY - OpenAI API key
"""

import os
import json
import argparse
from typing import Dict, List, Optional
from openai import OpenAI

class EmailWriterAgent:
    """Agent for generating sales outreach content."""
    
    STAGES = ["new", "follow_up", "reorder"]
    
    def __init__(self):
        """Initialize the agent with OpenAI client."""
        self.client = OpenAI()
    
    def generate_intro_email(self, store_info: Dict, brand_info: Dict) -> str:
        """
        Generate an introduction email for a new store.
        
        Args:
            store_info: Dictionary with store details
            brand_info: Dictionary with brand details
            
        Returns:
            Email text
        """
        prompt = f"""You are writing a professional but friendly sales email for a field sales rep.

STORE INFORMATION:
- Name: {store_info.get('store_name', 'the store')}
- Type: {store_info.get('store_type', 'retail store')}
- City: {store_info.get('city', '')}
- Notes: {store_info.get('notes', 'N/A')}

BRAND INFORMATION:
- Brand: {brand_info.get('brand_name', '')}
- Category: {brand_info.get('category', '')}
- Summary: {brand_info.get('summary', '')}
- Ideal Stores: {brand_info.get('ideal_stores', '')}
- Talking Points: {brand_info.get('talking_points', '')}

Write a brief introduction email (150-200 words) that:
1. Introduces yourself as a local sales rep
2. Mentions why this brand is a good fit for their store type
3. Highlights 1-2 key benefits or unique selling points
4. Suggests a quick call or visit to discuss
5. Keeps a friendly, conversational tone

Subject line should be short and relevant.

Format:
Subject: [subject line]

[email body]

Best regards,
[Your Name]
Field Sales Representative"""

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are an expert sales copywriter who creates personalized, effective outreach emails."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=400
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_text_script(self, store_info: Dict, brand_info: Dict) -> str:
        """
        Generate a text message or DM script.
        
        Args:
            store_info: Dictionary with store details
            brand_info: Dictionary with brand details
            
        Returns:
            Text message script
        """
        prompt = f"""You are writing a brief text message or Instagram DM for a field sales rep.

STORE INFORMATION:
- Name: {store_info.get('store_name', 'the store')}
- Type: {store_info.get('store_type', 'retail store')}

BRAND INFORMATION:
- Brand: {brand_info.get('brand_name', '')}
- Summary: {brand_info.get('summary', '')}

Write a very short text message (2-3 sentences, max 160 characters) that:
1. Introduces yourself briefly
2. Mentions the brand
3. Asks if they have a moment to chat
4. Sounds natural and conversational

Keep it casual and friendly, like you're texting a potential business partner."""

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are an expert at writing concise, friendly business text messages."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_call_script(self, store_info: Dict, brand_info: Dict) -> str:
        """
        Generate a call script with key questions.
        
        Args:
            store_info: Dictionary with store details
            brand_info: Dictionary with brand details
            
        Returns:
            Call script
        """
        prompt = f"""You are creating a call script for a field sales rep.

STORE INFORMATION:
- Name: {store_info.get('store_name', 'the store')}
- Type: {store_info.get('store_type', 'retail store')}
- Owner/Contact: {store_info.get('owner_contact', 'store owner')}

BRAND INFORMATION:
- Brand: {brand_info.get('brand_name', '')}
- Category: {brand_info.get('category', '')}
- Summary: {brand_info.get('summary', '')}
- Talking Points: {brand_info.get('talking_points', '')}
- Suggested Opening Order: {brand_info.get('suggested_opening_order', '')}

Create a call script with:

1. OPENING (brief introduction)
2. VALUE PROPOSITION (why this brand fits their store)
3. KEY QUESTIONS (4-5 discovery questions to ask)
4. OBJECTION RESPONSES (2-3 common objections and how to handle them)
5. CLOSING (suggest next steps)

Keep it conversational and natural, not overly scripted."""

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are an expert sales trainer who creates effective call scripts."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_follow_up_email(self, store_info: Dict, last_contact_notes: str) -> str:
        """
        Generate a follow-up email based on previous interaction.
        
        Args:
            store_info: Dictionary with store details
            last_contact_notes: Notes from last interaction
            
        Returns:
            Follow-up email text
        """
        prompt = f"""You are writing a follow-up email for a field sales rep.

STORE INFORMATION:
- Name: {store_info.get('store_name', 'the store')}
- Type: {store_info.get('store_type', 'retail store')}

LAST CONTACT NOTES:
{last_contact_notes}

Write a brief follow-up email (100-150 words) that:
1. References the previous conversation
2. Addresses any concerns or questions they had
3. Provides value (new info, sample offer, etc.)
4. Suggests a clear next step
5. Keeps it light and non-pushy

Subject line should reference the previous conversation.

Format:
Subject: [subject line]

[email body]

Best regards,
[Your Name]"""

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are an expert at writing effective follow-up emails that get responses."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=350
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_reorder_email(self, store_info: Dict, brand_info: Dict, last_order_info: Dict) -> str:
        """
        Generate a reorder reminder email.
        
        Args:
            store_info: Dictionary with store details
            brand_info: Dictionary with brand details
            last_order_info: Dictionary with last order details
            
        Returns:
            Reorder email text
        """
        prompt = f"""You are writing a reorder reminder email for a field sales rep.

STORE INFORMATION:
- Name: {store_info.get('store_name', 'the store')}
- Type: {store_info.get('store_type', 'retail store')}

BRAND INFORMATION:
- Brand: {brand_info.get('brand_name', '')}

LAST ORDER:
- Date: {last_order_info.get('order_date', '')}
- Products: {last_order_info.get('skus', '')}
- Cases: {last_order_info.get('cases', '')}

Write a brief reorder email (100-150 words) that:
1. Checks in on how the products are selling
2. Reminds them it's been about a month since their order
3. Offers to help with a reorder
4. Mentions any new products or promotions if relevant
5. Makes it easy to say yes

Subject line should be about reordering.

Format:
Subject: [subject line]

[email body]

Best regards,
[Your Name]"""

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are an expert at writing reorder emails that drive repeat business."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=350
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_all_outreach(self, store_info: Dict, brand_info: Dict, 
                            stage: str = "new", 
                            last_contact_notes: str = "",
                            last_order_info: Dict = None) -> Dict[str, str]:
        """
        Generate all outreach materials for a store.
        
        Args:
            store_info: Dictionary with store details
            brand_info: Dictionary with brand details
            stage: Stage of outreach (new, follow_up, reorder)
            last_contact_notes: Notes from last contact (for follow-up)
            last_order_info: Last order details (for reorder)
            
        Returns:
            Dictionary with all generated content
        """
        result = {}
        
        if stage == "new":
            result["intro_email"] = self.generate_intro_email(store_info, brand_info)
            result["text_script"] = self.generate_text_script(store_info, brand_info)
            result["call_script"] = self.generate_call_script(store_info, brand_info)
        
        elif stage == "follow_up":
            result["follow_up_email"] = self.generate_follow_up_email(store_info, last_contact_notes)
        
        elif stage == "reorder":
            if last_order_info:
                result["reorder_email"] = self.generate_reorder_email(store_info, brand_info, last_order_info)
        
        return result


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Generate sales outreach content")
    parser.add_argument("--store-name", required=True, help="Store name")
    parser.add_argument("--store-type", default="retail store", help="Type of store")
    parser.add_argument("--city", default="", help="City")
    parser.add_argument("--brand-name", required=True, help="Brand name")
    parser.add_argument("--brand-summary", default="", help="Brand summary")
    parser.add_argument("--stage", choices=["new", "follow_up", "reorder"], 
                       default="new", help="Outreach stage")
    parser.add_argument("--notes", default="", help="Last contact notes (for follow-up)")
    
    args = parser.parse_args()
    
    # Build info dictionaries
    store_info = {
        "store_name": args.store_name,
        "store_type": args.store_type,
        "city": args.city
    }
    
    brand_info = {
        "brand_name": args.brand_name,
        "summary": args.brand_summary,
        "talking_points": "High quality, great margins, proven seller"
    }
    
    # Initialize agent
    agent = EmailWriterAgent()
    
    # Generate content
    print(f"Generating {args.stage} outreach for {args.store_name}...\n")
    
    if args.stage == "new":
        print("=" * 60)
        print("INTRO EMAIL")
        print("=" * 60)
        print(agent.generate_intro_email(store_info, brand_info))
        print("\n" + "=" * 60)
        print("TEXT MESSAGE SCRIPT")
        print("=" * 60)
        print(agent.generate_text_script(store_info, brand_info))
        print("\n" + "=" * 60)
        print("CALL SCRIPT")
        print("=" * 60)
        print(agent.generate_call_script(store_info, brand_info))
    
    elif args.stage == "follow_up":
        print("=" * 60)
        print("FOLLOW-UP EMAIL")
        print("=" * 60)
        print(agent.generate_follow_up_email(store_info, args.notes))
    
    elif args.stage == "reorder":
        last_order = {
            "order_date": "2024-11-01",
            "skus": "Sample SKUs",
            "cases": "3"
        }
        print("=" * 60)
        print("REORDER EMAIL")
        print("=" * 60)
        print(agent.generate_reorder_email(store_info, brand_info, last_order))


if __name__ == "__main__":
    main()
