// RQ-DSN-003, RQ-DSN-004, RQ-DSN-005, DEC-DSN-002 (ADR-DSN-001)
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { CLASS } from "../src/ui/classes.ts";
import { buildStylesheet, componentCss, cssVar, toCss, toCustomProperty } from "../src/ui/stylesheet.ts";
import { contrastViolations, loadTokens } from "../src/ui/tokens.ts";
import type { TokenSet } from "../src/ui/tokens.ts";

const UI_SOURCE_DIR = new URL("../src/ui/", import.meta.url);
const TOKEN_NAME = "colour.surface.base";
const TOKEN_PROPERTY = "--colour-surface-base";
const GLOBAL_PROPERTY = "--colour-paper";
const RAW_VALUE = "#ffffff";
const FOUND_NONE = 0;
const COLOUR_LITERAL = /#[0-9a-fA-F]{3,8}\b/;
const COLOUR_FUNCTION = /\b(?:rgb|rgba|hsl|hsla)\(/;
const DIMENSION_LITERAL = /\b\d+(?:\.\d+)?(?:px|rem|em|ms|pt|vh|vw)\b/;
const DECLARATION = /^\s+([a-z-]+): (.+);$/gm;
const ZERO = "0";
const KEYWORD_VALUE = /^[a-z-]+(?: [a-z-]+)*$/;

/** A one-token-per-tier set to check the generated custom properties. */
const SAMPLE: TokenSet = {
  global: { "colour.paper": RAW_VALUE },
  semantic: { [TOKEN_NAME]: "{colour.paper}" },
  component: { "page.background": `{${TOKEN_NAME}}` },
  pairings: [],
};

/** The declaration values of a CSS text, keyed by nothing: one entry per `property: value;` line. */
function declarationValues(css: string): string[] {
  return [...css.matchAll(DECLARATION)].map((match) => match[2]);
}

// RQ-DSN-003
test("given a dotted token name, when its custom property is built, then dots become hyphens behind a double dash", () => {
  // Given a token name
  // When the custom property is built
  // Then dots are hyphens and the name starts with two dashes
  assert.equal(toCustomProperty(TOKEN_NAME), TOKEN_PROPERTY);
});

// RQ-DSN-003
test("given a token name, when a CSS reference is built, then it is a var() on its custom property", () => {
  // Given a token name
  // When the reference is built
  // Then it is var(--name)
  assert.equal(cssVar(TOKEN_NAME), `var(${TOKEN_PROPERTY})`);
});

// RQ-DSN-003
test("given a three-tier set, when the custom properties are generated, then every token is declared and aliases stay var() references", () => {
  // Given one token per tier
  // When the :root rule is generated
  const css = toCss(SAMPLE);
  // Then the global holds the raw value and each alias references the tier below
  assert.ok(css.startsWith(":root {"));
  assert.ok(css.includes(`${GLOBAL_PROPERTY}: ${RAW_VALUE};`));
  assert.ok(css.includes(`${TOKEN_PROPERTY}: ${cssVar("colour.paper")};`));
  assert.ok(css.includes(`${toCustomProperty("page.background")}: ${cssVar(TOKEN_NAME)};`));
});

// RQ-DSN-003
test("given the shipped tokens, when the custom properties are generated, then every token of every tier is declared", () => {
  // Given the shipped token source
  const tokens = loadTokens();
  // When the custom properties are generated
  const css = toCss(tokens);
  // Then each token name has its custom property
  for (const tier of [tokens.global, tokens.semantic, tokens.component]) {
    for (const name of Object.keys(tier)) {
      assert.ok(css.includes(`${toCustomProperty(name)}:`), name);
    }
  }
});

// RQ-DSN-003
test("given the component rules, when their selectors are listed, then every class of the catalogue has a rule", () => {
  // Given the class names shared with the views
  // When the component rules are generated
  const css = componentCss();
  // Then each class appears in a selector
  for (const className of Object.values(CLASS)) {
    assert.ok(css.includes(`.${className}`), className);
  }
});

// RQ-DSN-003
test("given the component rules, when their declaration values are read, then each is a var(), a keyword or zero", () => {
  // Given the generated component rules
  // When every declaration value is read
  const values = declarationValues(componentCss());
  // Then none holds a raw colour or dimension
  assert.ok(values.length > 0);
  for (const value of values) {
    const tokenised = value.includes("var(") || value === ZERO || KEYWORD_VALUE.test(value) || value.endsWith(` ${ZERO} auto`) || value === `${ZERO} auto`;
    assert.ok(tokenised, value);
  }
});

// RQ-DSN-003
test("given the shipped tokens, when the whole stylesheet is built, then the custom properties come before the component rules", () => {
  // Given the shipped token source
  const tokens = loadTokens();
  // When the stylesheet is built
  const css = buildStylesheet(tokens);
  // Then it is the token rule followed by the component rules
  assert.equal(css, toCss(tokens) + componentCss());
});

// RQ-DSN-004
test("given the shipped tokens, when every text and background pairing is checked, then none is below its minimum contrast", () => {
  // Given the shipped token source
  // When its declared pairings are checked
  // Then no pairing is reported
  assert.deepEqual(contrastViolations(loadTokens()), []);
});

// RQ-DSN-005
test("given the sources of the interface, when they are scanned for raw visual literals, then none is found", () => {
  // Given every TypeScript source under src/ui
  const files = readdirSync(UI_SOURCE_DIR).filter((name) => name.endsWith(".ts"));
  // When each is scanned for hex colours, colour functions and dimensions
  const offenders = files.filter((name) => {
    const text = readFileSync(new URL(name, UI_SOURCE_DIR), "utf-8");
    return COLOUR_LITERAL.test(text) || COLOUR_FUNCTION.test(text) || DIMENSION_LITERAL.test(text);
  });
  // Then no file holds one
  assert.equal(offenders.length, FOUND_NONE, offenders.join(", "));
});
