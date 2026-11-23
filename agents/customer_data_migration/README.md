Agent #4 — Customer Data Migration Assessment

Version: V0.1.0
Project: Customer Success AI Agent Library
Language: Python
Status: Read-Only Assessment Prototype

Overview

The Customer Data Migration Assessment Agent is the fourth component of a 12-agent Customer Success AI Agent Library.

It helps B2B SaaS Customer Success and Implementation teams assess migration requirements, identify missing information, detect migration risks, and generate proposed next steps.

Agent #4 integrates available outputs from the first three agents:

* Agent #1 — Sales-to-Customer-Success Handoff.
* Agent #2 — Customer Onboarding Planning.
* Agent #3 — Customer Onboarding Coordination.

The workflow produces structured JSON and human-readable Markdown reports.

Agent #4 does not execute customer data migrations or authorize migration execution.

Business Problem

Customer data migration can introduce uncertainty during SaaS onboarding.

Implementation teams may need to determine:

* Whether historical data migration is required.
* Which source systems contain relevant records.
* Who owns those systems.
* Whether access has been confirmed.
* Which datasets need to be assessed.
* Whether field mappings are available.
* Whether data-quality information is complete.
* Which risks remain unresolved.

When this information is missing, teams can struggle to assess migration readiness.

Agent #4 provides a structured assessment process that makes these gaps visible.

Core Capabilities

1. Upstream Source Integration

Loads available JSON outputs from Agents #1–3.

Checks deal identifiers and records missing or unverifiable sources.

2. Migration Requirement Extraction

Identifies potential migration requirements from selected sales handoff and onboarding planning information.

Requirements are treated as proposed until verified.

3. Source-System Inventory

Assesses supplied source-system and dataset information.

Flags missing ownership, access confirmation, record counts, and other inventory details.

4. Field Mapping Assessment

Evaluates supplied field mappings.

Identifies missing destination fields and unverified mappings.

5. Data-Quality Assessment

Checks whether essential dataset-level quality information has been documented.

This version does not independently profile source records.

6. Migration Risk Detection

Converts unresolved assessment findings into structured migration risks.

7. Migration Readiness Assessment

Classifies the current assessment using statuses such as:

* scope_not_established
* information_incomplete
* pending_human_review
* ready_for_review

A ready_for_review result is not permission to execute migration.

8. Migration Recommendations

Generates deterministic recommendations based on readiness and identified risks.

Recommendations are proposed and require human review.

9. Reporting

Produces:

* Structured JSON assessment reports.
* Human-readable Markdown reports.

10. CLI Workflow

Runs the assessment pipeline through a single terminal command.

Architecture

Agent #1 — Sales Handoff
             |
Agent #2 — Onboarding Planning
             |
Agent #3 — Onboarding Coordination
             |
             v
       Source Loader
             |
             v
    Requirement Extractor
             |
             v
      Source Inventory
             |
             v
     Mapping Assessment
             |
             v
   Data-Quality Assessment
             |
             v
       Risk Detection
             |
             v
    Readiness Assessment
             |
             v
  Recommendation Generator
             |
             v
       Report Generator
             |
       +-----+-----+
       |           |
       v           v
      JSON      Markdown

Project Structure

agents/customer_data_migration/
|
+-- __init__.py
+-- schemas.py
+-- source_loader.py
+-- requirement_extractor.py
+-- source_inventory.py
+-- mapping_rules.py
+-- data_quality_rules.py
+-- migration_risks.py
+-- readiness_assessment.py
+-- ai_migration_advisor.py
+-- report_generator.py
+-- markdown_renderer.py
+-- workflow.py
+-- README.md

Automated tests are located in:

tests/customer_data_migration/

Prerequisites

* Python environment compatible with the repository.
* Project dependencies installed.
* Access to the Customer Success AI Agent Library repository.
* Relevant upstream JSON outputs from Agents #1–3.

During development, the project was tested in a Python 3.15 environment.

Installation

From the repository root, activate the existing virtual environment:

source .venv/bin/activate

If dependencies are not installed, follow the repository’s project-level installation instructions.

Running Agent #4

Run the workflow from the repository root:

python -m agents.customer_data_migration.workflow \
  --deal-id 373031837427 \
  --customer-name "Northstar Software"

The command loads the available upstream agent outputs, performs the assessment, and generates reports.

Example Output

The Northstar Software synthetic scenario produced:

CUSTOMER DATA MIGRATION ASSESSMENT
----------------------------------
Deal ID: 373031837427
Customer: Northstar Software
Readiness: scope_not_established
Requirements: 0
Risks: 1
Recommendations: 1
Human review required: True
Migration authorized: False

The result means the current evidence has not established migration scope.

It does not mean that the customer has no migration requirements.

Generated Reports

The workflow creates:

outputs/customer_data_migration/
|
+-- migration_assessment_373031837427.json
|
+-- migration_assessment_373031837427.md

JSON Report

Contains structured information about:

* Customer and deal identity.
* Migration requirements.
* Source systems.
* Datasets.
* Field mappings.
* Migration risks.
* Readiness status.
* Recommendations.
* Approval information.
* Source-loading metadata.

Markdown Report

Provides a human-readable assessment covering the same major findings.

It includes an explicit advisory notice.

Testing

Run Agent #4 tests:

python -m pytest tests/customer_data_migration/ -v

Run the full repository test suite:

python -m pytest -q

The development process included synthetic tests for:

* Missing migration scope.
* Incomplete migration information.
* Ready-for-review recommendation generation.
* Report generation.
* CLI integration.

Human Review and Safety

Agent #4 preserves:

requires_human_review = True
migration_authorized = False

The workflow does not:

* Execute migrations.
* Modify customer source systems.
* Write records to destination systems.
* Independently inspect source data.
* Approve migration execution.
* Treat unverified findings as confirmed facts.

A human reviewer must evaluate the assessment and any proposed actions.

Current Limitations

* Requirement extraction uses deterministic text matching.
* The recommendation generator uses explicit Python rules rather than a live LLM.
* The CLI does not yet accept independently supplied migration inventories or field mappings.
* Data-quality checks evaluate assessment metadata, not actual customer records.
* Risk severity is not automatically determined from operational impact.
* Exact-match finding deduplication does not resolve all semantic overlaps.
* Source deal-ID checks do not independently establish document authenticity.
* The prototype does not provide production migration execution capabilities.

Future Improvements

Potential enhancements include:

1. Structured inputs for customer-confirmed inventories.
2. Verified field mapping workflows.
3. Stronger evidence provenance.
4. Controlled data-quality profiling.
5. Evidence-based risk prioritization.
6. LLM-assisted requirement interpretation.
7. Human approval workflows.
8. Production security and access controls.
9. Broader integration and performance testing.

Development Milestones

Version	Capability
V0.0.1	Project setup
V0.0.2	Migration schemas
V0.0.3	Upstream integration
V0.0.4	Requirement extraction
V0.0.5	Source inventory and mapping
V0.0.6	Data quality and risks
V0.0.7	Readiness assessment
V0.0.8	Recommendations
V0.0.9	JSON and Markdown reporting
V0.1.0	CLI integration

Position in the Agent Library

Agent #1 — Sales-to-CS Handoff
                |
                v
Agent #2 — Onboarding Planning
                |
                v
Agent #3 — Onboarding Coordination
                |
                v
Agent #4 — Customer Data Migration Assessment

Disclaimer

This project is an experimental, read-only migration assessment prototype.

It is not a production migration engine.

Generated findings and recommendations require human verification before operational decisions are made.