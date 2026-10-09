// RQ-DSN-001, RQ-DSN-002, RQ-DSN-004, DEC-DSN-001 (ADR-DSN-001)
import { test } from "node:test";
import assert from "node:assert/strict";
import { TOKENS_FILE_URL, TokenError, aliasTarget, contrastRatio, contrastViolations, loadTokens, relativeLuminance, resolveToken, tierOf, tierViolations } from "../src/ui/tokens.ts";
import type { TokenSet } from "../src/ui/tokens.ts";

const WHITE = "#ffffff";
const BLACK = "#000000";
const GREY = "#777777";
const MAX_CONTRAST = 21;
const CONTRAST_TOLERANCE = 0.01;
const GREY_ON_WHITE = 4.48;
const GLOBAL_NAME = "colour.ink";
const SEMANTIC_NAME = "colour.text.primary";
const COMPONENT_NAME = "button.text";
const MISSING_NAME = "colour.missing";
const CIRCULAR_ONE = "colour.loop.one";
const CIRCULAR_TWO = "colour.loop.two";
const NOT_A_COLOUR = "blue";
const ALIAS_TEXT = `{${GLOBAL_NAME}}`;

/** A small valid token set: one global, one semantic aliasing it, one component aliasing the semantic. */
function sampleTokens(overrides: Partial<TokenSet> = {}): TokenSet {
  return {
    global: { [GLOBAL_NAME]: BLACK, "colour.paper": WHITE },
    semantic: { [SEMANTIC_NAME]: ALIAS_TEXT, "colour.surface.base": "{colour.paper}" },
    component: { [COMPONENT_NAME]: `{${SEMANTIC_NAME}}` },
    pairings: [{ foreground: SEMANTIC_NAME, background: "colour.surface.base", minimum: 4.5 }],
    ...overrides,
  };
}

// RQ-DSN-002
test("given the shipped token source, when it is loaded, then the three tiers and the pairings are present", () => {
  // Given the file the design system ships
  // When it is loaded
  const tokens = loadTokens(TOKENS_FILE_URL);
  // Then every tier holds tokens and pairings are declared
  assert.ok(Object.keys(tokens.global).length > 0);
  assert.ok(Object.keys(tokens.semantic).length > 0);
  assert.ok(Object.keys(tokens.component).length > 0);
  assert.ok(tokens.pairings.length > 0);
});

// RQ-DSN-002
test("given a token name, when its tier is asked, then the defining tier is returned", () => {
  // Given a sample set
  const tokens = sampleTokens();
  // When the tier of each kind of name is asked
  // Then the tier is returned, and undefined for an unknown name
  assert.equal(tierOf(tokens, GLOBAL_NAME), "global");
  assert.equal(tierOf(tokens, SEMANTIC_NAME), "semantic");
  assert.equal(tierOf(tokens, COMPONENT_NAME), "component");
  assert.equal(tierOf(tokens, MISSING_NAME), undefined);
});

// RQ-DSN-002
test("given values with and without braces, when the alias target is read, then only an alias gives a name", () => {
  // Given an alias and a raw value
  // When the target is read
  // Then the alias gives the token name and the raw value gives undefined
  assert.equal(aliasTarget(ALIAS_TEXT), GLOBAL_NAME);
  assert.equal(aliasTarget(WHITE), undefined);
});

// RQ-DSN-002
test("given a component token, when it is resolved, then the chain ends on the raw value of the global tier", () => {
  // Given a component aliasing a semantic token aliasing a global token
  const tokens = sampleTokens();
  // When the component token is resolved
  const value = resolveToken(tokens, COMPONENT_NAME);
  // Then the raw global value comes back
  assert.equal(value, BLACK);
});

// RQ-DSN-002
test("given an unknown or circular token, when it is resolved, then a TokenError is thrown", () => {
  // Given an unknown name and two semantic tokens aliasing each other
  const tokens = sampleTokens({ semantic: { [CIRCULAR_ONE]: `{${CIRCULAR_TWO}}`, [CIRCULAR_TWO]: `{${CIRCULAR_ONE}}` } });
  // When each is resolved
  // Then a TokenError is thrown
  assert.throws(() => resolveToken(tokens, MISSING_NAME), TokenError);
  assert.throws(() => resolveToken(tokens, CIRCULAR_ONE), TokenError);
});

// RQ-DSN-002
test("given a valid three-tier set, when the tiers are validated, then no violation is reported", () => {
  // Given a set where each tier aliases the tier below
  // When it is validated
  // Then there is no violation
  assert.deepEqual(tierViolations(sampleTokens()), []);
});

// RQ-DSN-002
test("given a component holding a raw value or a global aliasing a token, when the tiers are validated, then each is reported", () => {
  // Given a component token with a raw value and a global token that is an alias
  const tokens = sampleTokens({ component: { [COMPONENT_NAME]: WHITE }, global: { [GLOBAL_NAME]: "{colour.paper}", "colour.paper": WHITE } });
  // When the tiers are validated
  const problems = tierViolations(tokens);
  // Then both tokens are named
  assert.ok(problems.some((problem) => problem.startsWith(COMPONENT_NAME)));
  assert.ok(problems.some((problem) => problem.startsWith(GLOBAL_NAME)));
});

// RQ-DSN-002
test("given a component aliasing a global token directly, when the tiers are validated, then the skipped tier is reported", () => {
  // Given a component that skips the semantic tier
  const tokens = sampleTokens({ component: { [COMPONENT_NAME]: ALIAS_TEXT } });
  // When the tiers are validated
  // Then the component is reported
  assert.ok(tierViolations(tokens).some((problem) => problem.startsWith(COMPONENT_NAME)));
});

// RQ-DSN-002
test("given the shipped token source, when its tiers are validated, then no violation is reported", () => {
  // Given the file the design system ships
  // When its tiers are validated
  // Then the chain is respected everywhere
  assert.deepEqual(tierViolations(loadTokens()), []);
});

// RQ-DSN-004
test("given white and black, when the relative luminance is computed, then it is 1 and 0", () => {
  // Given the two extreme colours
  // When their luminance is computed
  // Then white is 1 and black is 0
  assert.ok(Math.abs(relativeLuminance(WHITE) - 1) < CONTRAST_TOLERANCE);
  assert.equal(relativeLuminance(BLACK), 0);
});

// RQ-DSN-004
test("given a text that is not a #rrggbb colour, when the luminance is computed, then a TokenError is thrown", () => {
  // Given a colour name
  // When the luminance is computed
  // Then a TokenError is thrown
  assert.throws(() => relativeLuminance(NOT_A_COLOUR), TokenError);
});

// RQ-DSN-004
test("given black on white, when the contrast is computed, then it is the maximum and does not depend on the order", () => {
  // Given the two extreme colours
  // When the contrast is computed in both orders
  // Then it is 21:1 either way
  assert.ok(Math.abs(contrastRatio(BLACK, WHITE) - MAX_CONTRAST) < CONTRAST_TOLERANCE);
  assert.equal(contrastRatio(WHITE, BLACK), contrastRatio(BLACK, WHITE));
});

// RQ-DSN-004
test("given a mid grey on white, when the contrast is computed, then it is just under 4.5", () => {
  // Given #777777 on white
  // When the contrast is computed
  // Then it is about 4.48:1
  assert.ok(Math.abs(contrastRatio(GREY, WHITE) - GREY_ON_WHITE) < CONTRAST_TOLERANCE);
});

// RQ-DSN-004
test("given a pairing below its minimum, when the contrast is checked, then the pairing is reported", () => {
  // Given a text token whose colour is mid grey on a white surface
  const tokens = sampleTokens({ global: { [GLOBAL_NAME]: GREY, "colour.paper": WHITE } });
  // When the pairings are checked
  const problems = contrastViolations(tokens);
  // Then the pairing is named with its ratio
  assert.equal(problems.length, 1);
  assert.ok(problems[0].startsWith(SEMANTIC_NAME));
});

// RQ-DSN-004
test("given a pairing above its minimum, when the contrast is checked, then nothing is reported", () => {
  // Given black text on a white surface
  // When the pairings are checked
  // Then there is no violation
  assert.deepEqual(contrastViolations(sampleTokens()), []);
});
