Sales-to-Customer-Success Handoff AI Agent

An AI-assisted workflow built with Python, HubSpot, and OpenAI

Overview

The Sales-to-Customer-Success Handoff AI Agent is a Python-based project designed to improve the transition from a closed sales opportunity to customer onboarding.

During a typical sales cycle, valuable customer information is captured across CRM records, sales notes, and conversations. When responsibility transfers from Sales to Customer Success, important details may be incomplete, unclear, or difficult to locate.

This project explores how AI can help organize that information into a structured handoff report while preserving source references, identifying missing information, and requiring human review before the handoff is approved.

The agent assists with handoff preparation. It does not autonomously approve customer commitments or onboarding readiness.

The Problem

Sales-to-Customer-Success handoffs can suffer from several challenges:

* Customer expectations are scattered across CRM records and notes.
* Important onboarding details may be missing.
* Sales discussions may contain commitments that have not been formally confirmed.
* Customer Success teams may struggle to verify the source of information.
* Manual handoff preparation can be repetitive and inconsistent.

The goal of this project is to demonstrate a more structured, evidence-aware handoff workflow.

Key Features

1. HubSpot CRM Integration

The agent retrieves relevant deal information and associated sales notes from HubSpot.

The CRM data is normalized into a structured input for downstream processing.

2. AI-Powered Sales Intelligence Extraction

OpenAI is used to extract potentially useful handoff information from sales notes.

The extraction process helps organize customer context and identify information relevant to onboarding.

3. Missing Information Detection

The workflow checks for information gaps that could make a handoff difficult to review or act upon.

4. Onboarding Risk Identification

The agent highlights potential risks and areas requiring clarification before onboarding.

5. Source Reference Validation

Extracted facts can be linked to source-note identifiers.

The workflow checks whether those references correspond to source notes included in the saved handoff data.

This is an internal consistency check, not independent verification against HubSpot.

6. Evidence Availability Assessment

The agent checks whether extracted evidence is available in the saved handoff data.

When evidence excerpts are present, it can compare extracted evidence with those excerpts.

A matching excerpt does not establish that a claim is true. Missing or mismatched evidence is flagged for review.

7. Handoff Quality Scoring

The agent generates a rule-based quality assessment based on factors such as evidence availability, missing information, risks, and human-review safeguards.

The score is intended to guide review, not to certify handoff accuracy.

8. Review Recommendations

The workflow generates and prioritizes recommendations to help a human reviewer investigate missing, unclear, or unsupported information.

9. Markdown Handoff Reporting

The agent produces a structured Markdown report containing customer context, extracted intelligence, risks, evidence-review findings, and recommended next steps.

Reports are explicitly marked as drafts requiring human review.

Architecture

The workflow follows this general sequence:

HubSpot CRM → Data Retrieval and Normalization → OpenAI Extraction → Rule-Based Validation → Quality and Readiness Assessment → Markdown Report → Human Review

The project separates CRM integration, AI extraction, validation, reporting, and workflow execution into different modules.

This separation makes individual components easier to test and maintain.

Technology Stack

Technology	Purpose
Python	Core application and workflow orchestration
HubSpot API	CRM data retrieval
OpenAI API	AI-assisted information extraction
Requests	HTTP communication
Beautiful Soup	Processing HTML-formatted notes
python-dotenv	Local environment configuration
pytest	Automated testing
Markdown	Human-readable handoff reports

Project Structure

The main project directories include:

* agents/sales_handoff/ — Handoff workflow, extraction, validation, scoring, and reporting
* integrations/crm/ — CRM integration and data normalization
* tests/ — Automated tests
* docs/ — Project documentation
* evaluations/ — Evaluation-related project files
* sample_data/ — Sample-data directory
* shared/ — Shared project components

The root-level run_handoff.py file provides a simplified command-line entry point.

Getting Started

Prerequisites

You will need:

* Python installed locally
* Access to a HubSpot account and the necessary CRM API permissions for live execution
* An OpenAI API key for live AI extraction
* Git for cloning the repository

Installation

Clone the repository:

git clone https://github.com/manikabedi-pixel/customer-success-agent-library.git

Navigate to the project:

cd customer-success-agent-library

Create and activate a virtual environment:

python -m venv .venv
source .venv/bin/activate

Install the dependencies:

python -m pip install -r requirements.txt

Environment Configuration

Create a local .env file using .env.example as a reference.

Configure the required HubSpot and OpenAI credentials.

Never commit .env, API keys, customer data, or other sensitive information to version control.

Running the Agent

The project supports two execution modes.

Report Mode

Report mode uses an existing saved handoff JSON file to generate a Markdown report.

It does not need to retrieve new CRM data or call OpenAI.

Example:

python run_handoff.py --deal-id YOUR_DEAL_ID

Report mode is the default.

Important: A saved handoff JSON file for the specified deal must already exist in the expected output directory.

Live Mode

Live mode retrieves CRM information and performs AI-assisted handoff generation.

Example:

python run_handoff.py --deal-id YOUR_DEAL_ID --mode live

Live mode requires valid credentials, access to the relevant HubSpot records, and an available OpenAI API connection.

Generated Outputs

The workflow saves generated handoff artifacts in:

outputs/sales_handoff/

Depending on the execution mode, these may include structured JSON and Markdown reports.

The outputs/ directory is excluded from Git to reduce the risk of publishing customer information.

Testing

The project includes automated tests for handoff processing, validation, scoring, recommendations, reporting, and workflow behavior.

Run the test suite with:

python -m pytest -q

The project also includes checks for missing handoff files and malformed saved JSON.

Human-in-the-Loop Design

The agent is designed to support human decision-making.

Its reports identify information requiring review and do not represent final approval.

A human reviewer remains responsible for:

* Confirming customer expectations and commitments
* Investigating missing or inconsistent information
* Verifying claims against authoritative CRM records
* Assessing onboarding risks
* Approving the handoff before operational use

Limitations

This project is a working prototype and reference implementation, not a production-certified customer onboarding system.

Important limitations include:

* AI-generated extractions may be incomplete or incorrect.
* Source-reference validation checks internal consistency, not source authenticity.
* Evidence-excerpt matching does not independently establish factual accuracy.
* Older saved handoff files may lack evidence excerpts.
* Quality scores are heuristic and should not be interpreted as guarantees.
* Live execution depends on external API availability and permissions.
* Human review is required before relying on the generated report.

Project Status

Version: 1.0 — Initial project release

The current release demonstrates an AI-assisted handoff workflow with structured reporting, evidence-aware review, automated tests, and a simplified command-line interface.

Purpose

This project was developed to explore how AI agents can support Customer Success operations by reducing repetitive information organization while making uncertainty, evidence gaps, and human accountability visible.

The central design principle is:

AI prepares the handoff. Humans verify and approve it.