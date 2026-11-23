Agent #2 — Customer Onboarding Planning

Version: V0.1.0
Project: Customer Success AI Agent Library
Language: Python
Status: Prototype — Human Review Required

Overview

The Customer Onboarding Planning Agent is the second component of a 12-agent Customer Success AI Agent Library.

It helps B2B SaaS Customer Success teams transform structured sales handoff information into a proposed onboarding plan.

The agent uses the output of Agent #1 — Sales-to-Customer-Success Handoff — as its primary input.

It organizes onboarding objectives, milestones, tasks, dependencies, and planning information while identifying missing details that require human attention.

The agent does not autonomously approve or execute onboarding activities.

Business Problem

Customer Success teams often receive sales handoff information that must be manually converted into an actionable onboarding plan.

This can involve reviewing customer objectives, identifying implementation activities, creating milestones, and determining responsibilities.

When information is incomplete, teams may make assumptions about task ownership, timelines, or customer commitments.

Agent #2 provides a structured planning workflow that helps make these gaps visible.

Core Capabilities

* Consumes structured sales handoff information from Agent #1.
* Extracts available onboarding context and objectives.
* Creates proposed onboarding milestones and tasks.
* Evaluates task ownership and due-date completeness.
* Identifies missing planning information.
* Assesses onboarding dependencies and risks.
* Produces AI-assisted planning suggestions.
* Generates a structured onboarding plan.
* Preserves human-review and approval requirements.

Architecture

Agent #1 — Sales-to-CS Handoff
                |
                v
        Sales Handoff JSON
                |
                v
       Agent #2 — Planning
                |
                +-- Context Extraction
                |
                +-- Objective Identification
                |
                +-- Milestone Planning
                |
                +-- Task Planning
                |
                +-- Dependency Assessment
                |
                +-- Planning Risk Assessment
                |
                +-- AI Planning Suggestions
                |
                v
       Onboarding Plan JSON
                |
                v
          Human Review

Input

Agent #2 consumes a structured sales handoff JSON document.

Example:

outputs/sales_handoff/hubspot_handoff_<deal_id>.json

The handoff may contain customer information, deal context, sales intelligence, stakeholders, and onboarding risks.

Output

Agent #2 produces a structured onboarding plan.

Example:

outputs/onboarding_planning/onboarding_plan_<deal_id>.json

The output includes information such as:

* Customer and deal identifiers.
* Proposed onboarding objectives.
* Milestones.
* Tasks.
* Missing information.
* Planning assessment.
* Dependency assessment.
* AI planning suggestions.
* Human-review and approval status.

Example Development Scenario

A synthetic Northstar Software scenario was used during development.

The planning workflow produced:

Metric	Result
Proposed milestones	5
Proposed tasks	8
Approved for execution	No

The proposed tasks were not treated as automatically assigned or approved.

The agent preserved unresolved ownership and scheduling information for review.

Running the Agent

Run Agent #2 using the execution entry point provided by the repository.

The exact CLI arguments should be confirmed against the current implementation before publishing a copy-and-paste command.

The agent requires an appropriate Agent #1 handoff input.

Testing

Run the onboarding planning tests from the repository root:

python -m pytest tests/onboarding_planning/ -v

Run the complete repository suite:

python -m pytest -q

Human Review and Safety

The agent generates a proposed onboarding plan.

It does not automatically:

* Approve onboarding plans.
* Assign real team members.
* Commit customer-facing delivery dates.
* Execute onboarding activities.
* Confirm that unverified customer information is accurate.

Missing information and unresolved planning issues must be reviewed by an authorized person.

Current Limitations

* Planning quality depends on the completeness of the sales handoff.
* Proposed milestones and tasks require validation.
* Task ownership and deadlines may remain unresolved.
* The prototype does not guarantee that the plan is operationally executable.
* The workflow should not be treated as a replacement for implementation planning or customer approval.

Future Improvements

Potential enhancements include:

* More sophisticated dependency analysis.
* Customer-specific onboarding templates.
* Better task prioritization.
* Integration with project management platforms.
* Human approval workflows.
* Planning quality evaluation across different customer segments.

Position in the Agent Library

Agent #1 — Sales-to-CS Handoff
                |
                v
Agent #2 — Customer Onboarding Planning
                |
                v
Agent #3 — Customer Onboarding Coordination

Agent #2 provides the structured planning information used by Agent #3.

Disclaimer

This project is an experimental Customer Success automation prototype.

Generated plans and recommendations require human review before operational use.