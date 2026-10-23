// RQ-DSN-001, RQ-DSN-002, RQ-DSN-004, DEC-DSN-001 (ADR-DSN-001)
import { readFileSync } from "node:fs";

/** RQ-DSN-001: where the design-system source of truth lives, relative to this module. */
export const TOKENS_FILE_URL = new URL("../../design/tokens.json", import.meta.url);

const ALIAS_PATTERN = /^\{([^{}]+)\}$/;
const HEX_COLOUR_PATTERN = /^#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i;
const HEX_RADIX = 16;
const CHANNEL_MAX = 255;
const TOKEN_ERROR_NAME = "TokenError";
const TIER_GLOBAL = "global";
const TIER_SEMANTIC = "semantic";
const TIER_COMPONENT = "component";

/** WCAG 2.x relative luminance coefficients and thresholds (RQ-DSN-004). */
const LUMINANCE_RED = 0.2126;
const LUMINANCE_GREEN = 0.7152;
const LUMINANCE_BLUE = 0.0722;
const LINEAR_THRESHOLD = 0.04045;
const LINEAR_DIVISOR = 12.92;
const GAMMA_OFFSET = 0.055;
const GAMMA_DIVISOR = 1.055;
const GAMMA_EXPONENT = 2.4;
const CONTRAST_OFFSET = 0.05;

/** RQ-DSN-002: the three tiers of the token chain, from raw values to component usages. */
export type Tier = typeof TIER_GLOBAL | typeof TIER_SEMANTIC | typeof TIER_COMPONENT;

/** RQ-DSN-004: a foreground/background colour pairing with its minimum contrast ratio. */
export interface Pairing {
  readonly foreground: string;
  readonly background: string;
  readonly minimum: number;
}

/** RQ-DSN-001: the token source as stored in tokens.json. */
export interface TokenSet {
  readonly global: Readonly<Record<string, string>>;
  readonly semantic: Readonly<Record<string, string>>;
  readonly component: Readonly<Record<string, string>>;
  readonly pairings: readonly Pairing[];
}

/** RQ-DSN-001: a token name that no tier defines, or an alias chain that never reaches a global token. */
export class TokenError extends Error {
  constructor(message: string) {
    super(message);
    this.name = TOKEN_ERROR_NAME;
  }
}

export const GENERATION_ORDER: readonly Tier[] = [TIER_GLOBAL, TIER_SEMANTIC, TIER_COMPONENT];
const TIER_ORDER: readonly Tier[] = [...GENERATION_ORDER].reverse();
const TIER_TARGET: Readonly<Record<Tier, Tier | null>> = { [TIER_COMPONENT]: TIER_SEMANTIC, [TIER_SEMANTIC]: TIER_GLOBAL, [TIER_GLOBAL]: null };

/** RQ-DSN-001: reads and parses the token source; the file path is replaceable for tests. */
export function loadTokens(source: URL | string = TOKENS_FILE_URL): TokenSet {
  return JSON.parse(readFileSync(source, "utf-8")) as TokenSet;
}

/** RQ-DSN-002: the tier that defines a token name, or undefined when none does. */
export function tierOf(tokens: TokenSet, name: string): Tier | undefined {
  return TIER_ORDER.find((tier) => Object.hasOwn(tokens[tier], name));
}

/** RQ-DSN-002: the alias target of a value written {token.name}, or undefined for a raw value. */
export function aliasTarget(value: string): string | undefined {
  return ALIAS_PATTERN.exec(value)?.[1];
}

/** RQ-DSN-001: follows the alias chain of a token down to the raw value held by the global tier. */
export function resolveToken(tokens: TokenSet, name: string): string {
  const seen = new Set<string>();
  let current = name;
  for (;;) {
    const tier = tierOf(tokens, current);
    if (tier === undefined || seen.has(current)) {
      throw new TokenError(`unknown or circular token: ${current}`);
    }
    seen.add(current);
    const value = tokens[tier][current];
    const target = aliasTarget(value);
    if (target === undefined) {
      return value;
    }
    current = target;
  }
}

/** RQ-DSN-002: lists every token that breaks the chain (global raw, semantic to global, component to semantic). */
export function tierViolations(tokens: TokenSet): string[] {
  const problems: string[] = [];
  for (const tier of TIER_ORDER) {
    for (const [name, value] of Object.entries(tokens[tier])) {
      const target = aliasTarget(value);
      const expected = TIER_TARGET[tier];
      if (expected === null && target !== undefined) {
        problems.push(`${name}: a global token must hold a raw value`);
      } else if (expected !== null && (target === undefined || tierOf(tokens, target) !== expected)) {
        problems.push(`${name}: a ${tier} token must alias a ${expected} token`);
      }
    }
  }
  return problems;
}

/** RQ-DSN-004: the WCAG relative luminance of a #rrggbb colour. */
export function relativeLuminance(colour: string): number {
  const match = HEX_COLOUR_PATTERN.exec(colour);
  if (match === null) {
    throw new TokenError(`not a #rrggbb colour: ${colour}`);
  }
  const [red, green, blue] = [match[1], match[2], match[3]].map((channel) => toLinear(parseInt(channel, HEX_RADIX) / CHANNEL_MAX));
  return LUMINANCE_RED * red + LUMINANCE_GREEN * green + LUMINANCE_BLUE * blue;
}

function toLinear(channel: number): number {
  return channel <= LINEAR_THRESHOLD ? channel / LINEAR_DIVISOR : ((channel + GAMMA_OFFSET) / GAMMA_DIVISOR) ** GAMMA_EXPONENT;
}

/** RQ-DSN-004: the WCAG contrast ratio between two #rrggbb colours, from 1 up. */
export function contrastRatio(foreground: string, background: string): number {
  const [lighter, darker] = [relativeLuminance(foreground), relativeLuminance(background)].sort((a, b) => b - a);
  return (lighter + CONTRAST_OFFSET) / (darker + CONTRAST_OFFSET);
}

/** RQ-DSN-004: lists every declared pairing whose contrast ratio is below its minimum. */
export function contrastViolations(tokens: TokenSet): string[] {
  return tokens.pairings
    .map((pairing) => ({ pairing, ratio: contrastRatio(resolveToken(tokens, pairing.foreground), resolveToken(tokens, pairing.background)) }))
    .filter(({ pairing, ratio }) => ratio < pairing.minimum)
    .map(({ pairing, ratio }) => `${pairing.foreground} on ${pairing.background}: ${ratio.toFixed(1)} is below ${pairing.minimum}`);
}
