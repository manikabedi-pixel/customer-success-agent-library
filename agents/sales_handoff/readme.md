Agent #1 — Sales-to-Customer-Success Handoff

Version: V1.0
Project: Customer Success AI Agent Library
Language: Python
Status: Developed Prototype — Human Review Required

⸻

1. Overview

The Sales-to-Customer-Success Handoff Agent is the first component of a 12-agent Customer Success AI Agent Library.

It is designed to help B2B SaaS companies improve the transition from Sales to Customer Success by transforming available sales and deal information into a structured customer handoff.

The agent focuses on one of the most important transitions in the customer lifecycle:

The moment a customer moves from the sales process into onboarding.

During this transition, valuable information can be lost, overlooked, or communicated inconsistently.

Agent #1 helps organize that information into a reusable format that downstream Customer Success agents can consume.

The resulting handoff provides a foundation for onboarding planning, coordination, and migration assessment.

The agent supports human decision-making. It does not independently verify every sales claim, approve customer commitments, or authorize operational actions.

⸻

2. Business Problem

In many B2B SaaS organizations, Sales and Customer Success teams operate with different priorities.

Sales focuses on understanding customer requirements, progressing opportunities, and closing deals.

Customer Success focuses on delivering the promised experience, supporting onboarding, and helping customers achieve their objectives.

The transition between these functions can create information gaps.

Common challenges include:

* Customer objectives are not clearly documented.
* Important sales conversations are difficult to locate.
* Implementation expectations are not communicated consistently.
* Customer stakeholders and responsibilities are unclear.
* Risks identified during the sales process are overlooked.
* Customer Success teams spend time manually reviewing CRM records.
* Onboarding begins without a complete understanding of customer expectations.

These problems can create additional work for Customer Success Managers and implementation teams.

They can also increase the risk of misalignment between what was discussed during Sales and what the onboarding team understands.

The Objective

Agent #1 aims to make the sales handoff more structured, consistent, and reusable.

Instead of relying entirely on manual interpretation of sales information, the agent produces a structured handoff assessment that can support the next stage of the customer lifecycle.

⸻

3. Core Capabilities

3.1 Sales and Deal Context Processing

The agent processes available sales and deal information.

Relevant context may include:

* Customer identity.
* Deal identity.
* Customer requirements.
* Business objectives.
* Sales intelligence.
* Stakeholder information.
* Implementation expectations.
* Potential onboarding risks.

The exact information available depends on the source records.

3.2 Customer Context Organization

The agent organizes relevant customer information into a structured format.

This helps downstream workflows distinguish customer and deal details from onboarding-related findings.

3.3 Sales Intelligence Handoff

The agent preserves relevant sales intelligence for Customer Success review.

This may include information about customer objectives, expectations, or implementation considerations.

The handoff should not be interpreted as independent verification of every sales statement.

3.4 Onboarding Risk Visibility

The agent supports the identification and communication of risks that may affect onboarding.

These findings can help Customer Success teams identify issues requiring clarification before implementation activities begin.

3.5 Structured JSON Output

The agent produces a machine-readable JSON handoff.

This allows downstream agents to reuse the available context without requiring the entire sales handoff process to be repeated.

3.6 Human Review

The generated handoff is intended for human review.

Information that is incomplete, uncertain, or unverified should be confirmed by the appropriate team before it is used for consequential operational decisions.

⸻

4. Position in the Customer Success AI Agent Library

Agent #1 is the starting point for the current multi-agent workflow.

                 SALES PROCESS
                       |
                       v
          CRM / Sales Information
                       |
                       v
     +--------------------------------+
     |            AGENT #1            |
     |                                |
     |    Sales-to-CS Handoff Agent   |
     +--------------------------------+
                       |
                       v
          Structured Handoff JSON
                       |
                       v
     +--------------------------------+
     |            AGENT #2            |
     |                                |
     |    Customer Onboarding         |
     |    Planning                    |
     +--------------------------------+
                       |
                       v
     +--------------------------------+
     |            AGENT #3            |
     |                                |
     |    Customer Onboarding         |
     |    Coordination                |
     +--------------------------------+
                       |
                       v
     +--------------------------------+
     |            AGENT #4            |
     |                                |
     |    Customer Data Migration     |
     |    Assessment                  |
     +--------------------------------+

Agent #1 establishes the initial structured customer context.

Agent #2 uses that context to develop a proposed onboarding plan.

Agent #3 assesses onboarding coordination.

Agent #4 uses relevant upstream information to evaluate migration requirements and readiness.

This architecture supports the long-term goal of building connected Customer Success workflows rather than isolated automation tools.

⸻

5. High-Level Architecture

The conceptual workflow for Agent #1 is:

          CRM / Sales Information
                    |
                    v
           Source Data Loading
                    |
                    v
         Customer & Deal Context
                    |
                    v
        Sales Intelligence Review
                    |
                    v
         Handoff Risk Assessment
                    |
                    v
        Structured Handoff Output
                    |
                    v
              JSON Report
                    |
                    v
           Customer Success
              Human Review

This diagram represents the agent’s documented responsibilities rather than a verified one-to-one mapping of its current Python modules.

The exact implementation structure should be checked against the repository.

⸻

6. Input Data

Agent #1 uses available sales and deal information.

The development workflow included a HubSpot-oriented handoff output.

The input structure and required fields depend on the repository implementation.

Example Input Categories

Category	Information
Customer	Customer name and available account context
Deal	Deal identifier and relevant deal information
Sales intelligence	Customer objectives and requirements
Stakeholders	Available contact and stakeholder information
Implementation context	Relevant onboarding expectations
Risks	Known or suspected onboarding concerns

The agent should not be assumed to have access to information that is absent from its source records.

⸻

7. Output Data

Agent #1 produces a structured sales handoff JSON file.

The established development scenario used the following output:

outputs/sales_handoff/
    hubspot_handoff_373031837427.json

For other deals, the output filename may follow the same deal-based naming pattern.

Output Structure

The handoff contains structured customer and deal context used by downstream agents.

A key implementation detail is that the deal identifier is stored within a nested deal object.

Conceptually:

{
  "deal": {
    "id": "373031837427"
  },
  "sales_intelligence": {},
  "onboarding_risks": []
}

Note: This is an illustrative partial structure, not a complete copy of the generated JSON schema.

The actual output may contain additional fields and different nested structures.

Why Structured Output Matters

A machine-readable handoff makes it possible to:

1. Reuse customer context in onboarding planning.
2. Preserve references to the originating deal.
3. Support downstream assessment workflows.
4. Reduce repeated manual information gathering.
5. Build a more connected Customer Success automation architecture.

⸻

8. Example Development Scenario

During development, a synthetic customer scenario called Northstar Software was used across the agent library.

The associated deal ID was:

373031837427

Agent #1 produced a sales handoff file:

outputs/sales_handoff/
    hubspot_handoff_373031837427.json

This file became an upstream input for the later agents.

Downstream Usage

Agent #2 — Onboarding Planning

Used the sales handoff context to create a proposed onboarding plan.

Agent #3 — Onboarding Coordination

Assessed the onboarding plan produced by Agent #2.

Agent #4 — Customer Data Migration

Loaded the Agent #1 handoff alongside the available Agent #2 and Agent #3 outputs.

Agent #4 examined relevant sales intelligence for migration-related information.

In the Northstar Software scenario, the current migration requirement extractor identified zero established migration requirements.

That result did not prove migration was unnecessary.

Instead, Agent #4 classified the assessment as:

scope_not_established

It recommended confirming whether historical data migration was required.

This demonstrates why preserving structured sales context is useful for downstream workflows.

It also illustrates the importance of not interpreting missing information as a confirmed business decision.

⸻

9. Installation and Environment

Agent #1 is part of the Customer Success AI Agent Library repository.

Prerequisites

* Python.
* Access to the repository.
* Required project dependencies.
* An appropriate sales/deal data source or development fixture.

Activate the Virtual Environment

From the repository root:

cd ~/customer-success-agent-library

Activate the existing environment:

source .venv/bin/activate

If the virtual environment has not been created, follow the repository-level setup instructions.

Install Dependencies

Use the dependency management method defined by the repository.

Do not assume that the project uses a particular requirements file or package manager without checking the repository.

⸻

10. Running Agent #1

Run Agent #1 using the execution entry point provided by the repository.

The exact command should be verified against the current implementation before being added to this README.

To locate possible entry points, inspect the Agent #1 package and project documentation.

The workflow should produce a structured handoff output for the selected customer or deal.

Expected Output Location

For the established development scenario:

outputs/sales_handoff/
    hubspot_handoff_373031837427.json

Verify the Output

After running the agent, inspect the generated JSON file.

Confirm that:

* The correct deal is represented.
* Customer information is associated with the intended account.
* Relevant sales intelligence is present.
* Missing information is not presented as verified fact.
* The output can be consumed by downstream agents.

⸻

11. Testing

Testing is an important part of the Customer Success AI Agent Library.

For Agent #1, testing should cover:

* Source data handling.
* Customer and deal identification.
* Structured handoff generation.
* Missing information.
* Invalid input handling.
* Output serialization.
* Downstream compatibility.

Run the Full Repository Test Suite

From the repository root:

python -m pytest -q

Agent-Specific Tests

The exact Agent #1 test directory should be confirmed from the repository.

Once verified, the README can include the appropriate command for running only Agent #1 tests.

Important

This README does not claim a specific number of passing tests because the current Agent #1 test summary has not been verified here.

⸻

12. Human Review and Safety

Agent #1 supports the transfer of sales information into Customer Success.

However, the generated handoff should not be treated as an independently verified record of every customer commitment.

The agent does not automatically:

* Approve customer commitments.
* Confirm that all sales statements are accurate.
* Assign implementation responsibilities.
* Authorize onboarding execution.
* Guarantee that the handoff contains every relevant customer requirement.

Human review remains necessary.

Customer Success and Implementation teams should confirm important assumptions and unresolved information before making operational decisions.

⸻

13. Current Limitations

The current handoff workflow has several important boundaries.

Source Data Quality

The quality of the output depends on the information available in the sales source.

Missing or inaccurate sales information can affect downstream planning.

Verification

Structured information is not automatically verified information.

Customer objectives, requirements, and commitments may require confirmation.

Incomplete Context

The agent cannot guarantee that every relevant sales conversation or customer requirement has been captured.

Downstream Interpretation

Other agents must interpret the handoff carefully.

For example, Agent #4 should not conclude that data migration is unnecessary merely because the handoff does not explicitly mention migration.

Operational Approval

The handoff does not independently authorize onboarding or implementation activities.

⸻

14. Future Improvements

Potential improvements include:

Stronger Source Validation

Improve checks for missing, inconsistent, and unverifiable CRM information.

Evidence Provenance

Preserve clearer references to the source records supporting each finding.

Handoff Completeness Assessment

Introduce more explicit checks for required handoff information.

Customer Commitment Verification

Support workflows for reviewing and confirming important sales commitments.

Better Human Review

Provide structured approval and clarification processes.

Additional CRM Integrations

Extend support for other sales platforms where appropriate.

Multi-Agent Context Management

Improve how downstream agents consume verified customer context while preserving uncertainty.

These are potential enhancements rather than claims about current functionality.

⸻

15. Development Principles

Agent #1 establishes several principles that are relevant to the entire Customer Success AI Agent Library.

Principle 1: Preserve Customer Context

Information collected during Sales should be available to the teams responsible for delivering the customer experience.

Principle 2: Structure Information for Reuse

Machine-readable outputs make it easier for downstream workflows to consume customer context.

Principle 3: Preserve Uncertainty

Missing or unverified information should not be silently converted into confirmed facts.

Principle 4: Separate Recommendations From Approval

Automated findings should support human judgment rather than replace it.

Principle 5: Build Connected Workflows

Each agent should contribute to a broader Customer Success process.

⸻

16. The Customer Success AI Agent Library

The broader project aims to develop 12 connected agents addressing different stages of the customer lifecycle.

The first four components are:

Agent	Name	Version
Agent #1	Sales-to-Customer-Success Handoff	V1.0
Agent #2	Customer Onboarding Planning	V0.1.0
Agent #3	Customer Onboarding Coordination	V0.1.0
Agent #4	Customer Data Migration Assessment	V0.1.0

The project explores how structured automation and AI-assisted workflows can help B2B SaaS teams:

* Reduce repetitive Customer Success work.
* Improve information continuity.
* Identify onboarding risks earlier.
* Support more consistent operational processes.
* Make customer information easier to act upon.

These are project goals, not claims of independently measured business outcomes.

⸻

17. Disclaimer

This project is an experimental Customer Success automation system.

The generated sales handoff is intended to support Customer Success and Implementation teams.

It does not replace human verification of customer commitments, requirements, or operational decisions.

Customer information must be handled according to applicable security, privacy, and organizational requirements.

⸻

Part of the 12-Agent Customer Success AI Agent Library.