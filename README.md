# Autonomous Voice of Customer (VoC) Intelligence Agent

## Overview

This project implements an **Autonomous Voice of Customer (VoC) Intelligence Agent** that collects, analyzes, and interprets publicly available e-commerce reviews to generate actionable product insights.

The system ingests reviews, stores them in a SQLite database, analyzes sentiment and themes using an LLM, and produces automated reports. It also provides a **conversational agent** that allows users to query customer insights directly.

Example queries:

* Compare Product A and Product B on comfort
* What are the top complaints about Product A?
* How many reviews mention battery issues?
* What improvements should Product A prioritize?

---

# Key Design Decisions

## Why OpenClaw Was Not Used

The PRD suggested implementing the system using **ClawdBot/OpenClaw**. I explored this approach and attempted to align the system architecture with OpenClaw’s agent orchestration model.

However, several practical considerations influenced the final implementation:

**Local Runtime Dependency**
OpenClaw operates as a locally orchestrated agent framework where tools and model calls run through a local runtime environment.

**LLM Integration Costs**
OpenClaw requires integration with external LLM providers. Depending on usage, these integrations may introduce infrastructure costs.

**Local Data Privacy Considerations**
Because OpenClaw executes tools and model calls locally, it would operate directly on my personal development machine. To avoid unnecessary interaction with unrelated system resources, I chose not to run a full OpenClaw runtime locally.

Instead, the system implements a lightweight agent architecture using:

* **LangChain SQL Agent** for reasoning and tool orchestration
* **Groq LLM** for analysis and conversational responses
* **SQLite** for structured review storage

This preserves the **agent-driven architecture described in the PRD** while keeping the implementation lightweight and cost-efficient.

---

## Why Firecrawl Was Used

The PRD suggested scraping using **BeautifulSoup or Playwright**.
However, major e-commerce platforms such as **Amazon and Flipkart actively restrict traditional scraping methods** through dynamic rendering, anti-bot protections, and request blocking.

During testing, BeautifulSoup and Playwright frequently returned incomplete data or were blocked.

To address this, I used **Firecrawl**, which provides managed crawling infrastructure capable of extracting structured content from dynamic websites. Firecrawl also provides sufficient **free credits for development**, making it suitable for this sprint implementation.

---

## Weekly Delta Demonstration

The PRD requires detection of **new reviews added since the previous ingestion cycle**.

Because the project was developed within a short sprint timeframe, real weekly updates were not always available. To validate the pipeline, I simulated delta detection by reintroducing **page 1 reviews at the end of the ingestion process**, allowing the system to detect them as newly ingested records and generate a **Weekly Delta Report**.

---

# System Architecture

```text
Flipkart Reviews
       ↓
Firecrawl Scraping
       ↓
Data Cleaning
       ↓
SQLite Database
       ↓
Groq LLM Analysis
       ↓
LangChain SQL Agent
       ↓
Reports & Conversational Insights
```

---

# Project Structure

```
voc-agent-noise/
│
├ tools/
│   ├ flipkart_prodA.py
│   ├ flipkart_prodB.py
│   ├ db_insert.py
│   ├ analyze_reviews.py
│   ├ generate_report.py
│   └ soul-voc_agent.py
│
├ reviews.db
├ weekly_delta_report.py
├ global_voc_report.md
├ weekly_delta_report.md
├ README.md
├ SOUL.md
├ requirements.txt
└ .env
```

---

# Database Schema

Table: `reviews`

Columns:

* product
* rating
* title
* review_text
* date
* sentiment
* theme

---

# Setup

Install dependencies:

```
pip install -r requirements.txt
```

Create `.env` file:

```
GROQ_API_KEY=your_key
```

---

# Running the Pipeline

Scrape reviews:

```
python tools/flipkart_prodA.py
python tools/flipkart_prodB.py
```

Insert reviews:

```
python tools/db_insert.py
```

Analyze reviews:

```
python tools/analyze_reviews.py
```

---

# Generating Reports

Global report:

```
python tools/generate_report.py
```

Weekly delta report:

```
python weekly_delta_report.py
```

---

# Conversational VoC Agent

Run the conversational agent:

```
python tools/soul-voc_agent.py
```

Example:

```
You: Compare Product A and Product B on comfort

Agent:
Product B receives stronger positive feedback on comfort,
while Product A has several complaints related to fit.
```

The agent uses **LangChain SQL Agent + Groq** to generate SQL queries and provide grounded insights.

---

# Automation & Scheduling

The VoC pipeline is automatically scheduled using GitHub Actions.
Workflow configuration:

```
.github/workflows/voc_agent_pipeline.yml
```

This workflow schedules the pipeline to run automatically and performs:
Review scraping from Flipkart
Database updates with newly ingested reviews
Sentiment and theme analysis using the Groq LLM
Generation of:
Global VoC Action Report
Weekly Delta Report

This scheduled workflow demonstrates the autonomous execution capability required in the PRD, ensuring that new customer feedback is periodically ingested and analyzed without manual intervention.

---

# Agent Identity

The agent configuration and behavior are defined in:

```
SOUL.md
```

The agent acts as a **Voice of Customer analyst**, identifying patterns in review data and generating insights for product teams.
