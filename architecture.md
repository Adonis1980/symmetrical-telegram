# RepRally AI Sales Automation System - Architecture

## Overview

This system automates the RepRally sales workflow using a combination of CRM, Google Sheets, Zapier, and AI agents. The goal is to enable remote-first sales operations where AI handles research, writing, reminders, and reporting while the sales rep focuses on conversations and order placement.

## Technology Stack

### Core Platforms
- **CRM**: HubSpot (recommended for robust automation and free tier)
- **Database**: Google Sheets (for flexible data management and easy viewing)
- **Automation**: Zapier (connects all tools and triggers AI agents)
- **AI**: OpenAI GPT-4 via Zapier AI or direct API integration

### Alternative Options
- CRM: Pipedrive or Zoho CRM
- Automation: n8n (open-source alternative)
- Database: Airtable (more structured than Sheets)

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Data Sources                             │
│  • Store Lists (manual entry)                                │
│  • Brand Information (paste from RepRally)                   │
│  • Call/Visit Notes (voice or text)                          │
│  • Order Logs (from RepRally app)                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Google Sheets Database                      │
│  • Stores Table                                              │
│  • Brands Table                                              │
│  • Orders Table                                              │
│  • Activities Table                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    HubSpot CRM                               │
│  • Contacts (stores)                                         │
│  • Deals (sales pipeline)                                    │
│  • Tasks (reminders)                                         │
│  • Notes (AI-generated summaries)                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Zapier Automation Workflows                     │
│  • Trigger on new store → Agent 1                            │
│  • Trigger on new brand → Agent 2                            │
│  • Trigger on new lead → Agent 3                             │
│  • Trigger on notes entry → Agent 4                          │
│  • Scheduled daily → Agent 5                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    AI Agents (5)                             │
│  1. Store Research & Prep Agent                              │
│  2. Email & Follow-up Writer Agent                           │
│  3. Daily Route & Reminder Agent                             │
│  4. Order Entry Assistant Agent                              │
│  5. Weekly Report Generator Agent                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      Outputs                                 │
│  • Enriched store records in CRM                             │
│  • Ready-to-send emails and scripts                          │
│  • Daily task lists and reminders                            │
│  • Clean activity summaries                                  │
│  • Weekly performance reports                                │
└─────────────────────────────────────────────────────────────┘
```

## Data Model

### Stores Table (Google Sheets)
| Field | Type | Description |
|-------|------|-------------|
| Store ID | Text | Unique identifier |
| Store Name | Text | Business name |
| Owner/Contact | Text | Primary contact person |
| Phone | Text | Contact phone |
| Email | Text | Contact email |
| Instagram | Text | Social media handle |
| Website | URL | Store website |
| Address | Text | Full address |
| City | Text | City location |
| Store Type | Dropdown | liquor, c-store, smoke shop, cafe, wellness, etc. |
| Status | Dropdown | new, contacted, qualified, customer, inactive |
| First Contact Date | Date | When first reached out |
| Last Contact Date | Date | Most recent interaction |
| Notes | Text | General notes |

### Brands Table (Google Sheets)
| Field | Type | Description |
|-------|------|-------------|
| Brand ID | Text | Unique identifier |
| Brand Name | Text | Product brand name |
| Category | Text | Product category |
| Summary | Text | 3-4 sentence description |
| Ideal Stores | Text | Best store types |
| Ideal Customers | Text | Target customer profile |
| Talking Points | Text | Top 3-5 sales points |
| Suggested Opening Order | Text | SKUs and case quantities |
| Launch Date | Date | When brand was added |
| Status | Dropdown | active, seasonal, discontinued |

### Orders Table (Google Sheets)
| Field | Type | Description |
|-------|------|-------------|
| Order ID | Text | Unique identifier |
| Store ID | Text | Links to Stores table |
| Brand ID | Text | Links to Brands table |
| Order Date | Date | When order was placed |
| Cases | Number | Quantity ordered |
| SKUs | Text | Product SKUs ordered |
| Order Type | Dropdown | first, reorder |
| Next Reorder Date | Date | Calculated (21-35 days) |
| Notes | Text | Order-specific notes |

### Activities Table (Google Sheets)
| Field | Type | Description |
|-------|------|-------------|
| Activity ID | Text | Unique identifier |
| Store ID | Text | Links to Stores table |
| Activity Type | Dropdown | call, visit, email, text |
| Date | Date | When activity occurred |
| Raw Notes | Text | Original notes from rep |
| AI Summary | Text | Cleaned summary |
| Outcome | Dropdown | interested, maybe later, not a fit, ordered |
| Objections | Text | Any concerns raised |
| Next Step | Text | What to do next |
| Next Step Date | Date | When to follow up |

## AI Agent Specifications

### Agent 1: Store Research & Prep Agent
**Trigger**: New row added to Stores table with Name + City  
**Process**:
1. Search for store online (Google, social media)
2. Extract: phone, email, Instagram, website
3. Categorize store type
4. Update Stores table and create HubSpot contact

**Tech**: Zapier → AI by Zapier (web search + extraction) → Google Sheets + HubSpot

### Agent 2: Email & Follow-up Writer Agent
**Trigger**: New brand added OR new qualified store  
**Process**:
1. Read brand profile + store record
2. Generate intro email, text/DM script, call script
3. Save to HubSpot as note attached to contact
4. Create task for rep to review and send

**Tech**: Zapier → OpenAI API (GPT-4) → HubSpot

### Agent 3: Daily Route & Reminder Agent
**Trigger**: Daily at 7 AM  
**Process**:
1. Query Activities table for tasks due today
2. Query Orders table for reorders due this week
3. Generate prioritized task list
4. Send email/SMS to rep with daily plan

**Tech**: Zapier Schedule → Google Sheets → AI formatting → Email/SMS

### Agent 4: Order Entry Assistant Agent
**Trigger**: New order logged in Orders table  
**Process**:
1. Calculate next reorder date (21-35 days)
2. Update store status to "customer"
3. Create reorder reminder task in HubSpot
4. Log activity in Activities table

**Tech**: Zapier → Google Sheets → HubSpot

### Agent 5: Weekly Report Generator Agent
**Trigger**: Weekly on Monday at 9 AM  
**Process**:
1. Pull data from past week: new stores, orders, activities
2. Calculate metrics: conversion rate, orders by brand, reorders
3. Generate formatted report
4. Email to rep

**Tech**: Zapier Schedule → Google Sheets → AI summary → Email

## Implementation Phases

### Phase 1: Setup Foundation (Week 1)
- Create Google Sheets with all tables
- Set up HubSpot CRM account
- Configure Zapier account
- Connect all platforms

### Phase 2: Build Core Agents (Week 2)
- Agent 1: Store Research
- Agent 2: Email Writer
- Test with sample data

### Phase 3: Build Supporting Agents (Week 3)
- Agent 3: Daily Reminders
- Agent 4: Order Assistant
- Agent 5: Weekly Reports

### Phase 4: Testing & Refinement (Week 4)
- Run full workflow with real data
- Adjust prompts and logic
- Train user on system

## Security & Privacy Considerations

- Store API keys securely in Zapier
- Use HubSpot's built-in security features
- Limit Google Sheets sharing to necessary users only
- Regularly backup data
- Comply with data protection regulations (GDPR, CCPA)

## Cost Estimate

- **HubSpot CRM**: Free tier (up to 1M contacts)
- **Google Sheets**: Free
- **Zapier**: Starter plan $29.99/month (750 tasks/month) or Professional $73.50/month (2,000 tasks/month)
- **OpenAI API**: ~$10-30/month depending on usage

**Total**: $30-75/month

## Success Metrics

- **Time saved**: 10-15 hours/week on admin tasks
- **Response time**: Outreach within 24 hours of new lead
- **Reorder rate**: 80%+ of customers reorder within 35 days
- **Data quality**: 95%+ of store records complete
- **User satisfaction**: Rep can work from home 3-4 days/week
