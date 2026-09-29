import { createHash } from "node:crypto";

import type { TechnicalArchitectInput } from "./contracts.js";

function normalize(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value.map((item) => normalize(item));
  }

  if (value !== null && typeof value === "object") {
    const record = value as Record<string, unknown>;
    const normalized: Record<string, unknown> = {};

    for (const key of Object.keys(record).sort()) {
      normalized[key] = normalize(record[key]);
    }

    return normalized;
  }

  return value;
}

export function canonicalJson(value: unknown): string {
  return JSON.stringify(normalize(value));
}

export function fingerprintTechnicalArchitectInput(
  input: TechnicalArchitectInput,
): string {
  const hex = createHash("sha256")
    .update(canonicalJson(input), "utf8")
    .digest("hex");

  return `sha256:${hex}`;
}
