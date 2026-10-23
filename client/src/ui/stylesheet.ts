// RQ-DSN-003, RQ-DSN-005, DEC-DSN-002 (ADR-DSN-001)
import { CLASS } from "./classes.ts";
import { GENERATION_ORDER, aliasTarget } from "./tokens.ts";
import type { TokenSet } from "./tokens.ts";

const CUSTOM_PROPERTY_PREFIX = "--";
const NAME_SEPARATOR = ".";
const CSS_NAME_SEPARATOR = "-";
const CSS_ROOT_OPEN = ":root {\n";
const CSS_ROOT_CLOSE = "}\n";
const CSS_INDENT = "  ";

/** RQ-DSN-003: the CSS custom property name of a token, `colour.surface.base` giving `--colour-surface-base`. */
export function toCustomProperty(name: string): string {
  return CUSTOM_PROPERTY_PREFIX + name.split(NAME_SEPARATOR).join(CSS_NAME_SEPARATOR);
}

/** RQ-DSN-003: a CSS reference to a token. */
export function cssVar(name: string): string {
  return `var(${toCustomProperty(name)})`;
}

/** RQ-DSN-003: the :root rule exposing every token; aliases stay var() references so the chain survives in CSS. */
export function toCss(tokens: TokenSet): string {
  const lines: string[] = [];
  for (const tier of GENERATION_ORDER) {
    for (const [name, value] of Object.entries(tokens[tier])) {
      const target = aliasTarget(value);
      lines.push(`${CSS_INDENT}${toCustomProperty(name)}: ${target === undefined ? value : cssVar(target)};\n`);
    }
  }
  return CSS_ROOT_OPEN + lines.join("") + CSS_ROOT_CLOSE;
}

/** RQ-DSN-005: shorthands for the tokens that several rules share; every value is a var() on a token. */
const STROKE = cssVar("stroke.thin");
const STRONG = cssVar("text.strong.weight");
const CAPTION = cssVar("text.caption.size");
const FOCUS_OUTLINE = `${cssVar("focus.ring.width")} solid ${cssVar("focus.ring.colour")}`;
const SOLID_EDGE = `${STROKE} solid`;
const FLEX = { display: "flex" } as const;
const GRID = { display: "grid" } as const;
const FLEX_COLUMN = { ...FLEX, flexDirection: "column" } as const;
const UPPER_CASE_LETTER = /[A-Z]/g;
const HYPHEN = "-";

/** RQ-DSN-005: the CSS property of a camelCase key, `borderRadius` giving `border-radius`. */
function toProperty(key: string): string {
  return key.replace(UPPER_CASE_LETTER, (letter) => HYPHEN + letter.toLowerCase());
}

/** RQ-DSN-005: one rule, a selector and its declarations, each declaration naming a property and its value. */
function rule(selector: string, declarations: Record<string, string>): string {
  const body = Object.entries(declarations).map(([property, value]) => `  ${property}: ${value};\n`).join("");
  return `${selector} {\n${body}}\n`;
}

/** RQ-DSN-005: the descendant selector of a class, for the markup the views produce. */
function dot(className: string): string {
  return `.${className}`;
}

/** RQ-DSN-005: the component rules of the design-system catalogue, written only with var() references on tokens. */
export function componentCss(): string {
  return [
    rule("*, *::before, *::after", { boxSizing: "border-box" }),
    rule("body", {
      margin: "0",
      background: cssVar("page.background"),
      color: cssVar("page.text"),
      fontFamily: cssVar("text.family"),
      fontSize: cssVar("text.body.size"),
      fontWeight: cssVar("text.body.weight"),
      lineHeight: cssVar("text.body.leading"),
    }),
    rule(dot(CLASS.page), {
      maxWidth: cssVar("page.maxWidth"),
      margin: "0 auto",
      padding: cssVar("page.padding"),
      ...FLEX_COLUMN,
      gap: cssVar("page.gap"),
    }),
    rule(dot(CLASS.pageHeader), FLEX_COLUMN),
    rule(dot(CLASS.title), {
      margin: "0",
      fontSize: cssVar("text.title.size"),
      lineHeight: cssVar("text.title.leading"),
      fontWeight: STRONG,
    }),
    rule(dot(CLASS.heading), { margin: "0", fontSize: cssVar("text.heading.size"), fontWeight: STRONG }),
    rule(dot(CLASS.caption), { margin: "0", fontSize: CAPTION, color: cssVar("text.caption.color") }),
    rule(dot(CLASS.card), {
      background: cssVar("card.background"),
      border: `${SOLID_EDGE} ${cssVar("card.border")}`,
      borderRadius: cssVar("card.radius"),
      padding: cssVar("card.padding"),
      ...FLEX_COLUMN,
      gap: cssVar("card.gap"),
    }),
    rule(dot(CLASS.table), { width: cssVar("table.width"), borderCollapse: "collapse" }),
    rule(`${dot(CLASS.table)} th, ${dot(CLASS.table)} td`, {
      textAlign: "left",
      padding: cssVar("table.cellPadding"),
      borderBottom: `${SOLID_EDGE} ${cssVar("table.rowBorder")}`,
    }),
    rule(`${dot(CLASS.table)} th`, {
      background: cssVar("table.headerBackground"),
      color: cssVar("table.headerText"),
      fontSize: CAPTION,
      fontWeight: STRONG,
    }),
    rule(dot(CLASS.badge), {
      display: "inline-block",
      padding: `${cssVar("badge.paddingBlock")} ${cssVar("badge.paddingInline")}`,
      borderRadius: cssVar("badge.radius"),
      fontSize: CAPTION,
      fontWeight: STRONG,
    }),
    rule(dot(CLASS.badgeOpen), { background: cssVar("badge.open.background"), color: cssVar("badge.open.text") }),
    rule(dot(CLASS.badgeClosed), { background: cssVar("badge.closed.background"), color: cssVar("badge.closed.text") }),
    rule(dot(CLASS.banner), {
      ...FLEX_COLUMN,
      gap: cssVar("banner.gap"),
      padding: cssVar("banner.padding"),
      borderRadius: cssVar("banner.radius"),
    }),
    bannerRule(CLASS.bannerSuccess, "banner.success"),
    bannerRule(CLASS.bannerError, "banner.error"),
    bannerRule(CLASS.bannerWarning, "banner.warning"),
    rule(dot(CLASS.form), { ...GRID, gap: cssVar("card.gap") }),
    rule(dot(CLASS.field), { ...GRID, gap: cssVar("field.gap") }),
    rule(dot(CLASS.fieldLabel), { color: cssVar("field.label"), fontSize: CAPTION, fontWeight: STRONG }),
    rule(dot(CLASS.fieldControl), {
      minHeight: cssVar("field.minHeight"),
      padding: cssVar("field.padding"),
      background: cssVar("field.background"),
      color: cssVar("field.text"),
      border: `${SOLID_EDGE} ${cssVar("field.border")}`,
      borderRadius: cssVar("field.radius"),
      font: "inherit",
    }),
    rule(`${dot(CLASS.fieldControl)}:focus`, { outline: FOCUS_OUTLINE, borderColor: cssVar("field.borderFocus") }),
    rule(dot(CLASS.actions), { ...FLEX, gap: cssVar("space.tight") }),
    rule(dot(CLASS.button), {
      minHeight: cssVar("button.minHeight"),
      padding: `${cssVar("button.paddingBlock")} ${cssVar("button.paddingInline")}`,
      borderRadius: cssVar("button.radius"),
      border: `${SOLID_EDGE} transparent`,
      font: "inherit",
      fontWeight: STRONG,
      cursor: "pointer",
      transition: `background-color ${cssVar("button.transition")}`,
    }),
    rule(`${dot(CLASS.button)}:focus-visible`, { outline: FOCUS_OUTLINE }),
    rule(dot(CLASS.buttonPrimary), { background: cssVar("button.primary.background"), color: cssVar("button.primary.text") }),
    rule(`${dot(CLASS.buttonPrimary)}:hover`, { background: cssVar("button.primary.backgroundHover") }),
    rule(dot(CLASS.buttonSecondary), {
      background: cssVar("button.secondary.background"),
      color: cssVar("button.secondary.text"),
      borderColor: cssVar("button.secondary.border"),
    }),
    rule(`${dot(CLASS.buttonSecondary)}:hover`, { background: cssVar("button.secondary.backgroundHover") }),
    rule(dot(CLASS.buttonDanger), { background: cssVar("button.danger.background"), color: cssVar("button.danger.text") }),
  ].join("");
}

/** RQ-DSN-005: a banner variant, coloured by its background and text tokens with a border in the text colour. */
function bannerRule(className: string, tokenPrefix: string): string {
  const text = cssVar(`${tokenPrefix}.text`);
  return rule(dot(className), {
    background: cssVar(`${tokenPrefix}.background`),
    color: text,
    border: `${SOLID_EDGE} ${text}`,
  });
}

/** RQ-DSN-003: the whole stylesheet served to the browser, the token custom properties then the component rules. */
export function buildStylesheet(tokens: TokenSet): string {
  return toCss(tokens) + componentCss();
}
