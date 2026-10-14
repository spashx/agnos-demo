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
Tokens are declared in exactly one file, `client/design/tokens.json`, in three tiers: component tokens
(`button.primary.background`) alias semantic tokens (`colour.accent.default`) which alias global tokens
(`colour.blue.600`). An alias is written `{token.name}`.

| Tier | Pattern | Example |
|---|---|---|
| Global | `<category>.<family>.<step>` | `colour.slate.900`, `size.space.4` |
| Semantic | `<category>.<role>.<variant?>` | `colour.surface.elevated`, `space.default` |
| Component | `<component>.<part>.<state?>` | `button.primary.backgroundHover` |

#### 2.1 Colour
- **Global palette** (closed set): white; slate 50, 100, 300, 500, 700, 900; blue 600, 700; green 50, 700;
  red 50, 700; amber 50, 800.
- **Semantic roles**: `surface.base`, `surface.elevated`, `surface.recessed`, `border.default`, `focus.ring`,
  `text.primary`, `text.secondary`, `text.disabled`, `text.onAccent`, `accent.default`, `accent.hover`, and one
  `strong` and one `surface` token for each status: `success`, `error`, `warning`.
- **Theming**: light theme only in this release. Component tokens are theme-independent because they alias
  the semantic tier, so a dark theme later only remaps semantic tokens.
- **User-overridable colours**: none.

#### 2.2 Typography
- **Font family**: system sans-serif stack (`font.family.sans`); no web font is downloaded.
- **Type scale** by role: `type.title` (1.75rem, strong, tight leading), `type.heading` (1.25rem),
  `type.body` (1rem, normal leading 1.5), `type.caption` (0.875rem).
- **Dynamic fit**: no text is shrunk to fit; long values wrap.

#### 2.3 Spacing and layout grid
- **Base unit**: 0.25rem. Global steps `size.space.1`, 2, 3, 4, 6, 8 (0.25 to 2rem).
- **Spacing scale** by name: `space.hairline`, `space.tight`, `space.inline`, `space.default`, `space.loose`,
  `space.section`. Components reference the name, never the step.
- **Scaling model**: all sizes are in `rem`, so they follow the user's font size; only strokes are in pixels.

#### 2.4 Geometry
- **Corner radius**: `radius.soft` (0.25rem) for controls, `radius.round` (0.5rem) for cards and badges.
- **Stroke**: `stroke.thin` (1px) for borders, `stroke.thick` (2px) for the focus ring.
- **Elevation**: flat, no shadow. Cards are separated by a border.
- **Targets and layout**: `target.min` (2.75rem) minimum control height; `layout.content` (48rem) page width.

#### 2.5 Iconography and imagery
- **Style**: no icon set and no image. Two Unicode symbols, a check mark and a cross, accompany the
  open and closed states so they never rely on colour alone.
- **Sourcing**: text glyphs only, so they stay crisp at any zoom.

#### 2.6 Motion and timing
- **Duration scale**: `motion.hover` (120ms) for control colour changes, `motion.fade` (200ms) reserved for
  banners appearing.
- **Easing**: the browser default for both.
- **When not to animate**: a result (booking confirmed or refused) appears at once; it is never animated.

### 3. Component interaction states
| State | Trigger | Visual rule | Notes |
|---|---|---|---|
| Idle | no interaction | component tokens of the resting state | |
| Hover | pointer over a button | `button.*.backgroundHover`, eased by `button.transition` | no effect without a pointer |
| Active | pointer down | same as hover | no extra rule |
| Focused | keyboard focus on a control | outline `focus.ring.width` in `focus.ring.colour` | always visible, never colour alone: it is a 2px outline |
| Disabled | option or control unavailable | `colour.text.disabled` text | the reason is also written (for example "closed") |
| Selected | chosen option | the browser's native selection | no custom rule |
| Error | refused request | error banner (`banner.error.*`) | text states the cause |

### 4. Component catalogue
#### Page and Card
| Field | Value |
|---|---|
| Anatomy | page column, card with heading and content |
| States implemented | Idle |
| Tokens used | `page.background`, `page.text`, `page.maxWidth`, `page.padding`, `page.gap`, `card.background`, `card.border`, `card.padding`, `card.radius`, `card.gap` |
| Variants | none |

#### Button
| Field | Value |
|---|---|
| Anatomy | label in a padded box |
| States implemented | Idle, Hover, Focused |
| Tokens used | `button.primary.*`, `button.secondary.*`, `button.danger.*`, `button.paddingBlock`, `button.paddingInline`, `button.minHeight`, `button.radius`, `button.transition` |
| Variants | primary (the main action of a card), secondary (an alternative action), danger (undoes something done) |

#### Field
| Field | Value |
|---|---|
| Anatomy | label above a control (text, number, date and time, or list) |
| States implemented | Idle, Focused, Disabled |
| Tokens used | `field.background`, `field.border`, `field.borderFocus`, `field.text`, `field.label`, `field.padding`, `field.minHeight`, `field.radius`, `field.gap` |
| Variants | none |

#### Table
| Field | Value |
|---|---|
| Anatomy | header row, body rows separated by a thin border |
| States implemented | Idle |
| Tokens used | `table.headerBackground`, `table.headerText`, `table.rowBorder`, `table.cellPadding`, `table.width` |
| Variants | none |

#### Badge
| Field | Value |
|---|---|
| Anatomy | short text with a symbol on a tinted background |
| States implemented | Idle |
| Tokens used | `badge.open.*`, `badge.closed.*`, `badge.paddingBlock`, `badge.paddingInline`, `badge.radius` |
| Variants | open, closed |

#### Banner
| Field | Value |
|---|---|
| Anatomy | message on a tinted background, with an optional action below it |
| States implemented | Idle |
| Tokens used | `banner.success.*`, `banner.error.*`, `banner.warning.*`, `banner.padding`, `banner.radius`, `banner.gap` |
| Variants | success, error, warning |

#### Behaviour owners
To be completed when the first screens exist: each component will name the requirement that owns its behaviour. This catalogue owns appearance only.

### 5. Layout patterns
- **Single column page**: one centred column of at most `layout.content`, cards stacked with `page.gap`.
- **Card**: a heading then its content; the heading is the only way to name a card.
- **Stacked form**: one field per row, label above its control, the actions row at the end.

### 6. Accessibility and ergonomics
- **Contrast**: at least 4.5:1 for every text pairing; the pairings are declared in `tokens.json` (`pairings`)
  and verified by a test (RQ-DSN-004). Disabled text is exempt, as WCAG allows.
- **Minimum hit target**: `target.min` (2.75rem, 44 CSS pixels at the default font size) for buttons and fields.
- **Resizability**: sizes in `rem` and a fluid column; the page stays usable at 200% zoom.
- **Never colour alone**: badges carry a word and a symbol, banners carry text and an ARIA role, focus is an outline.

### 7. Framework binding
#### 7.1 Token module
`client/design/tokens.json` holds the tokens. `client/src/ui/tokens.ts` reads it with no window and no
browser, resolves aliases and checks tiers and contrast. Spec name to CSS name: dots become hyphens behind
two dashes, so `colour.surface.base` is `--colour-surface-base`.

#### 7.2 Rendering integration
`client/src/ui/stylesheet.ts` generates a `:root` rule with every token (aliases kept as `var()` references)
then the component rules, written only with `var()`. The server sends it as `/styles.css`; the views write
the class names declared once in `client/src/ui/classes.ts`.

#### 7.3 State-to-code mapping
Hover is `:hover`, keyboard focus is `:focus` on fields and `:focus-visible` on buttons, disabled is the
`disabled` attribute of an option.

#### 7.4 Prototyping and mockup sync
Screens are described in `client/design/SCREENS.md` with token names, never values, so there is no second
palette to drift. The UX designer reviews every change of `tokens.json`.

### 8. Testability
- **Headless verification**: token loading, alias resolution, tier chain, contrast ratios, custom property
  generation, component rules (`tests/tokens.test.ts`, `tests/stylesheet.test.ts`).
- **Regression check**: the same stylesheet test scans every source under `client/src/ui/` for hexadecimal
  colours, colour functions and dimensions (RQ-DSN-005); it is part of the Definition of Done of any UI change.
- **Visual verification**: the rendering in a browser is reviewed by the UX designer.

### 9. Governance
- **Adding a token**: propose it in `tokens.json` with its tier, name and value, add the pairing if it is a
  text colour, and use it in the same change.
- **Changing a value**: never needs a call-site edit; if it does, the token structure has a bug.
- **Deviating from a mockup value**: record a note in the `notes` entry of `tokens.json` with the rationale.
- **Deprecating a token**: grep for zero remaining references first, then remove it.
- **Document ownership**: the UX designer approves changes to this design system.

### 10. Non-goals
- No behaviour: what a button does belongs to the functional requirements of the screens.
- No dark theme, no icon set and no breakpoints in this release.

### Appendix: good and bad examples
| Bad | Good | Why |
|---|---|---|
| `color: #92400e;` in the stylesheet | `color: var(--banner-warning-text);` | Raw literal against a token (rule 1) |
| `padding: 12px;` on a field | `padding: var(--field-padding);` | Raw size against a token (rule 2) |
| a second constant for the success green | the `colour.success.strong` token | Same value under two names (rule 4) |
| `"button.primary.background": "#2563eb"` | `"button.primary.background": "{colour.accent.default}"` | A component token holding a raw value (rule 3) |
