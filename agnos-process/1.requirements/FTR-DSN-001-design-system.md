# FTR-DSN-001: Design system

## Overview
Roombook gets a web interface. Before its first screen is written, the team
needs a design system: one machine-readable source of truth for every visual decision (colours, typography,
spacing, geometry, motion), consumed by code as tokens, as the process demands for any project with a user
interface. This feature is that design system, instantiated from the `agnos-design-system` template; its
requirements make it checkable, its sections 0 to 10 are the document designers and developers follow.

## Stakeholders
- **Owner**: UX designer of Roombook
- **Consumers**: Developers and testers of the Roombook web interface; the product owner reviewing screens

---

## Functional Requirements

### RQ-DSN-001: Single token source
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The design system SHALL define every colour, typeface, size, spacing, radius, stroke and
  duration used by the interface as a named token in one machine-readable file, `client/design/tokens.json`.
- **Rationale**: One source of truth keeps the interface consistent and lets code and tests read the same values.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** the token file
  - **When** it is loaded by code with no window and no browser
  - **Then** every token of the three tiers is available by name
  - **And** an unknown token name is refused with an error
- **Dependencies**: None

### RQ-DSN-002: Tiered token chain
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The design system SHALL organise tokens in three tiers: global tokens hold the only raw
  values, semantic tokens alias a global token, and component tokens alias a semantic token.
- **Rationale**: Re-theming or adjusting a value is then a one-place edit instead of a search through the code.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** the token file
  - **When** the tier of each token is checked
  - **Then** no semantic or component token holds a raw value
  - **And** every component token aliases a semantic token
- **Dependencies**: RQ-DSN-001

### RQ-DSN-003: Stylesheet generation from tokens
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the web interface is served, the stylesheet it sends SHALL be generated from the token
  file, exposing every token as a CSS custom property and styling every component with those properties only.
- **Rationale**: A hand-written stylesheet would drift from the token source.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** the token file
  - **When** the stylesheet is generated
  - **Then** each token has a custom property, with aliases kept as references to the tier below
  - **And** each component rule takes its values from custom properties
- **Dependencies**: RQ-DSN-001, RQ-DSN-002

---

## Non-Functional Requirements

### RQ-DSN-004: Text contrast ratio
- **Category**: Non-Functional
- **NFR Type**: Accessibility
- **EARS Type**: Unwanted-behavior
- **Statement**: IF a declared text and background colour pairing has a contrast ratio below 4.5:1, THEN the
  design-system check SHALL fail.
- **Metric**: Contrast ratio of every declared pairing at least 4.5:1.
- **Measurement Method**: Unit test computing the WCAG contrast ratio of each pairing declared in the token file.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** a pairing of a text token and a surface token
  - **When** its contrast ratio is computed
  - **Then** a ratio below 4.5:1 is reported with the names of both tokens
  - **And** the shipped token file reports no pairing
- **Dependencies**: RQ-DSN-001

### RQ-DSN-005: Raw visual literal exclusion
- **Category**: Non-Functional
- **NFR Type**: Maintainability
- **EARS Type**: Unwanted-behavior
- **Statement**: IF a source file of the interface holds a raw colour or dimension literal, THEN the literal
  check SHALL fail the test run.
- **Metric**: 0 hexadecimal colour, colour function or dimension literal in the interface sources.
- **Measurement Method**: Unit test scanning the sources under `client/src/ui/` with regular expressions.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** the TypeScript sources of the interface
  - **When** they are scanned for hexadecimal colours, colour functions and dimensions
  - **Then** no file holds one
- **Dependencies**: RQ-DSN-002, RQ-DSN-003

---

## Design System
### 0. Agent operating rules
Before writing a visual literal, resolve it through the token chain, never skipping a tier:

```
Need a colour/size/duration/radius for new or changed UI code
  |
  +- 1. Does an existing COMPONENT token already name this exact thing?
  |     -> yes: use it. Done.
  |
  +- 2. Does an existing SEMANTIC token fit the role (surface, text, border, accent, status)?
  |     -> yes: reference it directly, or add a component token that aliases it.
  |
  +- 3. No existing token fits.
  |     -> reusable: add a SEMANTIC token to tokens.json and to section 2 below, then use it.
  |     -> truly one-off: a named local constant AND a COMPONENT token recorded in section 4.
  |
  +- 4. NEVER invent a new GLOBAL entry while implementing a component. Global tokens are a
        closed set curated by the UX designer; if a component seems to need a new base colour or
        size, stop and ask.
```

Hard rules, checked by grep or test (a violation is a defect):
1. No raw colour literal (`#rrggbb`, `rgb(...)`) outside `client/design/tokens.json` (RQ-DSN-005).
2. No raw size, spacing, radius, stroke or duration literal outside it either.
3. Every component token resolves to a semantic token, every semantic token to a global token (RQ-DSN-002).
4. Two components needing the same-looking thing share one token; the same value under two names is a defect.
5. A state rule (hover, focus, disabled, selected, error) not in section 3 is added to section 3 first.

When genuinely blocked (no token fits, not clearly one-off, not obviously a new role), stop and ask.

### 1. Purpose and principles
- **P1 Legible**: every text on its surface reaches the contrast of RQ-DSN-004, checked by a pairing list, not by eye.
- **P2 One accent**: a single interactive colour (`colour.accent.default`); the only other hues are the three status families.
- **P3 Never colour alone**: every status shows a word and a symbol next to its colour.
- **P4 Easy to hit**: every interactive control is at least `target.min` high.
- **P5 Tokens only**: no visual value exists outside `tokens.json`.

### 2. Foundations (design tokens)
To be written by the UX designer (RQ-DSN-001).

### 3. Component interaction states
To be written by the UX designer (RQ-DSN-001).

### 4. Component catalogue
To be written by the UX designer (RQ-DSN-001).

### 5. Layout patterns
To be written by the UX designer (RQ-DSN-001).

### 6. Accessibility and ergonomics
To be written by the UX designer (RQ-DSN-001).

### 7. Framework binding
To be written by the UX designer (RQ-DSN-001).

### 8. Testability
To be written by the UX designer (RQ-DSN-001).

### 9. Governance
To be written by the UX designer (RQ-DSN-001).

### 10. Non-goals
To be written by the UX designer (RQ-DSN-001).

### Appendix: good and bad examples
To be written by the UX designer (RQ-DSN-001).
