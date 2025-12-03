# AI-Powered RepRally Sales Automation System

This project provides a suite of 5 AI agents and automations to create a "remote-first" sales machine for RepRally sales representatives. The system handles research, writing, reminders, and reporting, allowing the sales rep to focus on building relationships, talking to stores, and placing orders.

This system is built using a combination of a CRM (HubSpot), a spreadsheet database (Google Sheets), an automation platform (Zapier), and AI models from OpenAI.

## Table of Contents

- [System Overview](#system-overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [The 5 AI Agents](#the-5-ai-agents)
- [Getting Started](#getting-started)
- [Usage Workflow](#usage-workflow)
- [Customization](#customization)
- [Project Structure](#project-structure)

## System Overview

The goal of this system is to automate the manual and time-consuming tasks of a sales job, such as:

- Researching and enriching new sales leads.
- Writing personalized outreach emails and scripts.
- Keeping track of follow-ups and reorder schedules.
- Summarizing call and visit notes.
- Generating weekly performance reports.

By automating these tasks, a sales rep can manage their territory more efficiently, reduce administrative overhead, and focus on high-value activities like customer interaction and closing deals.

## Features

- **Automated Lead Enrichment**: Automatically find contact information, social media profiles, and store types for new leads.
- **AI-Powered Content Generation**: Generate brand summaries, sales pitches, emails, text messages, and call scripts.
- **Intelligent Task Management**: Get daily reminders for calls, visits, and reorders, prioritized for you.
- **Effortless Note Summarization**: Turn rough call notes into structured CRM updates with clear next steps.
- **Proactive Reorder & Campaign Planning**: Automatically get reminders for reorders and suggestions for new brand launch campaigns.
- **Weekly Performance Reporting**: Receive a detailed weekly report with key metrics, insights, and recommendations.

## Technology Stack

- **CRM**: [HubSpot](https://www.hubspot.com/) (Free tier available)
- **Spreadsheet Database**: [Google Sheets](https://www.google.com/sheets/about/)
- **Automation**: [Zapier](https://zapier.com/) (Starter plan recommended)
- **AI**: [OpenAI](https://openai.com/) (GPT-4 models)

## System Architecture

The system is designed around a central data flow managed by Zapier, which connects Google Sheets, HubSpot, and OpenAI.

1.  **Data Input**: New stores, brands, notes, and orders are entered into Google Sheets or the CRM.
2.  **Zapier Triggers**: Zapier workflows are triggered by these new entries.
3.  **AI Agents**: The Zaps call the appropriate AI agent (via OpenAI API) to perform a task (e.g., research, writing).
4.  **Data Update**: The AI-generated output is used to update Google Sheets and HubSpot with enriched data, new tasks, and notes.
5.  **Notifications**: The sales rep is notified via email or SMS with daily plans, completed tasks, and weekly reports.

For a detailed architecture diagram, see the [Architecture Document](./docs/architecture.md).

## The 5 AI Agents

This system is composed of five specialized AI agents:

1.  **Agent 1: Store Research & Prep Agent**: Enriches new store leads with contact details and categorizes them.
2.  **Agent 2: Email & Follow-up Writer Agent**: Writes personalized outreach emails, texts, and call scripts.
3.  **Agent 3: Daily Route & Reminder Agent**: Generates a prioritized daily task list of calls, visits, and reorders.
4.  **Agent 4: Order Entry Assistant Agent**: Processes new orders, calculates reorder dates, and creates follow-up tasks.
5.  **Agent 5: Weekly Report Generator Agent**: Compiles a weekly sales report with metrics and AI-generated insights.

## Getting Started

To get this system up and running, follow the detailed instructions in the **[SETUP.md](./docs/SETUP.md)** guide. The setup process involves:

1.  **Prerequisites**: Signing up for HubSpot, Google, Zapier, and OpenAI accounts.
2.  **Google Sheets Setup**: Creating the required sheets and tables.
3.  **HubSpot Setup**: Configuring custom properties.
4.  **Zapier Setup**: Importing and configuring the provided Zapier workflow templates.
5.  **Connecting Accounts**: Linking all your accounts within Zapier.

## Usage Workflow

Here is a typical day-to-day workflow using the system:

1.  **Add New Stores**: Add a new store's name and city to the `Stores` sheet. Agent 1 will automatically research it and create a CRM contact.
2.  **Add New Brands**: Paste new brand information into the `Brands` sheet. Agent 2 will create a structured brand profile.
3.  **Outreach**: When a new lead is ready, Agent 2 automatically generates outreach materials and creates a task for you in HubSpot. You review, customize, and send.
4.  **Log Notes**: After a call or visit, you add your rough notes to the CRM. Agent 4 summarizes them and sets the next follow-up task.
5.  **Log Orders**: When you place an order in the RepRally app, you log the key details in the `Orders` sheet. Agent 4 calculates the reorder date and schedules a reminder.
6.  **Daily Briefing**: Each morning, Agent 3 sends you a prioritized list of your day's tasks.
7.  **Weekly Review**: Every Monday, Agent 5 sends you a comprehensive report on your previous week's performance.

## Customization

The system is designed to be flexible. You can customize:

- **Prompts**: All AI prompts are located in the Zapier workflow configurations and can be edited to change the tone, style, or content of the AI-generated text.
- **Business Logic**: Reorder windows, task priorities, and other business logic are defined in the Python scripts and Zapier workflows and can be adjusted to fit your needs.
- **Tools**: While this guide uses HubSpot, Google Sheets, and Zapier, the core logic can be adapted to other CRMs (Pipedrive, Zoho), databases (Airtable), or automation platforms (n8n).

## Project Structure

```
/home/ubuntu/reprally-ai-agents/
├── agents/                  # Python scripts for each AI agent
│   ├── agent1_store_research.py
│   ├── agent2_email_writer.py
│   ├── agent3_daily_reminders.py
│   ├── agent4_order_assistant.py
│   └── agent5_weekly_reports.py
├── docs/                    # Documentation files
│   ├── architecture.md
│   └── SETUP.md
├── templates/               # Google Sheets templates (to be created)
├── workflows/               # Zapier workflow configurations (JSON)
│   ├── agent1_zapier_workflow.json
│   ├── agent2_zapier_workflow.json
│   ├── agent3_zapier_workflow.json
│   ├── agent4_zapier_workflow.json
│   └── agent5_zapier_workflow.json
└── README.md                # This file
```
