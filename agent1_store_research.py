#!/usr/bin/env python3
"""
Agent 1: Store Research & Prep Agent

Purpose: Automatically enrich store records with contact information and categorization.

Trigger: New store added to Google Sheets with Name + City
Process:
1. Search for store online
2. Extract: phone, email, Instagram, website
3. Categorize store type
4. Update Google Sheets and HubSpot CRM

Usage:
    python3 agent1_store_research.py --store-name "ABC Liquor" --city "Miami"
    
Environment Variables Required:
    OPENAI_API_KEY - OpenAI API key
    GOOGLE_SHEETS_CREDS - Path to Google Sheets credentials JSON
    HUBSPOT_API_KEY - HubSpot API key
"""

import os
import json
import argparse
from typing import Dict, Optional
from openai import OpenAI

class StoreResearchAgent:
    """Agent for researching and enriching store information."""
    
    STORE_TYPES = [
        "liquor store",
        "convenience store (c-store)",
        "smoke shop",
        "cafe/coffee shop",
        "wellness store",
        "dispensary",
        "grocery store",
        "specialty retail",
        "gas station",
        "other"
    ]
    
    def __init__(self):
        """Initialize the agent with API clients."""
        self.client = OpenAI()  # Uses OPENAI_API_KEY from environment
        
    def research_store(self, store_name: str, city: str) -> Dict[str, str]:
        """
        Research a store and extract contact information.
        
        Args:
            store_name: Name of the store
            city: City where store is located
            
        Returns:
            Dictionary with enriched store information
        """
        
        # Create a comprehensive research prompt
        research_prompt = f"""You are a sales research assistant helping to find contact information for retail stores.

Store to research:
- Name: {store_name}
- City: {city}

Please provide the following information in JSON format:

{{
    "store_name": "{store_name}",
    "phone": "phone number if found, or 'Not found'",
    "email": "email address if found, or 'Not found'",
    "instagram": "Instagram handle without @ if found, or 'Not found'",
    "website": "website URL if found, or 'Not found'",
    "full_address": "complete street address if found, or 'Not found'",
    "store_type": "one of: {', '.join(self.STORE_TYPES)}",
    "confidence": "high/medium/low based on how certain you are about the information",
    "notes": "any relevant notes about the store, products they carry, or business focus"
}}

Important guidelines:
1. For store_type, choose the category that best fits based on what products they likely sell
2. If you're not certain about information, mark it as "Not found" rather than guessing
3. For Instagram, provide just the handle without the @ symbol
4. For website, include the full URL with https://
5. In notes, mention any relevant details about their product focus (alcohol, tobacco, wellness products, etc.)

Provide only the JSON object, no additional text."""

        try:
            # Call OpenAI to research the store
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful research assistant that finds accurate business information. You provide structured data in JSON format."},
                    {"role": "user", "content": research_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # Parse the response
            result_text = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if result_text.startswith("```json"):
                result_text = result_text.replace("```json", "").replace("```", "").strip()
            elif result_text.startswith("```"):
                result_text = result_text.replace("```", "").strip()
            
            result = json.loads(result_text)
            
            # Add metadata
            result["city"] = city
            result["status"] = "new"
            result["enrichment_date"] = self._get_current_date()
            
            return result
            
        except Exception as e:
            print(f"Error during research: {str(e)}")
            return {
                "store_name": store_name,
                "city": city,
                "phone": "Error",
                "email": "Error",
                "instagram": "Error",
                "website": "Error",
                "full_address": "Error",
                "store_type": "other",
                "confidence": "low",
                "notes": f"Error during research: {str(e)}",
                "status": "needs_review",
                "enrichment_date": self._get_current_date()
            }
    
    def categorize_store(self, store_info: Dict[str, str]) -> str:
        """
        Categorize the store type based on available information.
        
        Args:
            store_info: Dictionary with store information
            
        Returns:
            Store category
        """
        # This is handled in the main research function
        return store_info.get("store_type", "other")
    
    def format_for_google_sheets(self, store_data: Dict[str, str]) -> list:
        """
        Format store data for Google Sheets row.
        
        Args:
            store_data: Dictionary with store information
            
        Returns:
            List of values for Google Sheets row
        """
        return [
            self._generate_store_id(store_data["store_name"], store_data["city"]),
            store_data.get("store_name", ""),
            store_data.get("owner_contact", ""),  # Will be filled manually or in follow-up
            store_data.get("phone", ""),
            store_data.get("email", ""),
            store_data.get("instagram", ""),
            store_data.get("website", ""),
            store_data.get("full_address", ""),
            store_data.get("city", ""),
            store_data.get("store_type", ""),
            store_data.get("status", "new"),
            store_data.get("enrichment_date", ""),
            "",  # last_contact_date
            store_data.get("notes", "")
        ]
    
    def format_for_hubspot(self, store_data: Dict[str, str]) -> Dict:
        """
        Format store data for HubSpot CRM contact.
        
        Args:
            store_data: Dictionary with store information
            
        Returns:
            Dictionary formatted for HubSpot API
        """
        properties = {
            "company": store_data.get("store_name", ""),
            "phone": store_data.get("phone", ""),
            "email": store_data.get("email", ""),
            "website": store_data.get("website", ""),
            "address": store_data.get("full_address", ""),
            "city": store_data.get("city", ""),
            "store_type": store_data.get("store_type", ""),
            "lifecyclestage": "lead",
            "notes": store_data.get("notes", "")
        }
        
        # Add custom properties
        if store_data.get("instagram"):
            properties["instagram_handle"] = store_data.get("instagram")
        
        return {"properties": properties}
    
    def _generate_store_id(self, store_name: str, city: str) -> str:
        """Generate a unique store ID."""
        import hashlib
        raw = f"{store_name.lower().strip()}_{city.lower().strip()}"
        return hashlib.md5(raw.encode()).hexdigest()[:8].upper()
    
    def _get_current_date(self) -> str:
        """Get current date in YYYY-MM-DD format."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Research and enrich store information")
    parser.add_argument("--store-name", required=True, help="Name of the store")
    parser.add_argument("--city", required=True, help="City where store is located")
    parser.add_argument("--output", choices=["json", "sheets", "hubspot"], default="json",
                       help="Output format")
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = StoreResearchAgent()
    
    # Research the store
    print(f"Researching: {args.store_name} in {args.city}...")
    result = agent.research_store(args.store_name, args.city)
    
    # Output based on format
    if args.output == "json":
        print(json.dumps(result, indent=2))
    elif args.output == "sheets":
        row = agent.format_for_google_sheets(result)
        print("Google Sheets row:")
        print(row)
    elif args.output == "hubspot":
        contact = agent.format_for_hubspot(result)
        print("HubSpot contact:")
        print(json.dumps(contact, indent=2))
    
    print(f"\nConfidence level: {result.get('confidence', 'unknown')}")


if __name__ == "__main__":
    main()
