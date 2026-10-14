# PLAN-DSN-001: Design system

## Overview
Delivers the code side of the design system: the token module that loads and checks the token file, and the
generator of the stylesheet, as decided in ADR-DSN-001. The token file and the design-system document are
the UX designer's deliverables in FTR-DSN-001.

## References
- **Requirements**: RQ-DSN-001, RQ-DSN-002, RQ-DSN-003, RQ-DSN-004, RQ-DSN-005
- **ADRs**: ADR-DSN-001 (DEC-DSN-001, DEC-DSN-002)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-DSN-001: Implement token module
- **Tier**: M
- **Status**: Done
- **Description**: Add the module that loads the token file, resolves alias chains, rejects a token that
  breaks the three-tier chain and computes the contrast ratio of the declared text and background pairings.
- **Requirement refs**: RQ-DSN-001, RQ-DSN-002, RQ-DSN-004
- **ADR refs**: ADR-DSN-001 (DEC-DSN-001)
- **Acceptance Criteria** (Gherkin):
  - **Given** the token file with its three tiers and its pairings
  - **When** it is loaded and a component token is resolved
  - **Then** the chain ends on the raw value of the global tier
  - **And** a token that skips a tier, or a pairing below its minimum, is reported by name
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `node --test tests/tokens.test.ts` (in `client/`): 15 passed, 0 failed.
- **Assumptions**: Contrast is the WCAG 2.x ratio on colours written as `#rrggbb`.

### TASK-DSN-002: Implement stylesheet generator
- **Tier**: M
- **Status**: Done
- **Description**: Add the generator that exposes every token as a CSS custom property and writes the
  component rules of the catalogue with `var()` references only, plus the shared class names.
- **Requirement refs**: RQ-DSN-003, RQ-DSN-004, RQ-DSN-005
- **ADR refs**: ADR-DSN-001 (DEC-DSN-002)
- **Acceptance Criteria** (Gherkin):
  - **Given** the shipped token file
  - **When** the stylesheet is generated
  - **Then** each token has a custom property and each component rule uses `var()` only
  - **And** a scan of the interface sources finds no raw colour or dimension literal
- **Dependencies**: TASK-DSN-001, TASK-DSN-003
- **Assignee**: AI
- **Verification**: `node --test tests/stylesheet.test.ts` (in `client/`): 9 passed, 0 failed.
- **Assumptions**: The component rules are generated in TypeScript and sent by the server; no CSS file is stored.

### TASK-DSN-003: Raise warning text contrast
- **Tier**: S
- **Status**: Done
- **Description**: The contrast test failed on the warning text (amber 600 on amber 50, 3.07:1). Add amber 800
  to the global palette, point the warning token at it (6.84:1) and record the deviation note in the token file.
- **Requirement refs**: RQ-DSN-004
- **ADR refs**: None
- **Acceptance Criteria** (Gherkin):
  - **Given** the warning text and warning surface tokens
  - **When** the contrast ratio of their pairing is computed
  - **Then** it is at least 4.5:1
- **Dependencies**: TASK-DSN-001
- **Assignee**: Human
- **Verification**: N/A (Tier S)
- **Assumptions**: None
