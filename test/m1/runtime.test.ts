import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import test from "node:test";

import type { TechnicalArchitectInput } from "../../src/m1/contracts.js";
import { fingerprintTechnicalArchitectInput } from "../../src/m1/fingerprint.js";
import { FixtureProvider } from "../../src/m1/fixture-provider.js";
import { executeTechnicalArchitect } from "../../src/m1/runtime.js";

async function readJson(path: string): Promise<unknown> {
  return JSON.parse(await readFile(join(process.cwd(), path), "utf8")) as unknown;
}

async function readCaseInput(caseId: string): Promise<TechnicalArchitectInput> {
  const value = await readJson(
    `evals/m1/technical-architect/${caseId}.json`,
  );

  if (value === null || typeof value !== "object" || !("input" in value)) {
    throw new TypeError(`${caseId}: expected case object with input`);
  }

  return (value as { input: TechnicalArchitectInput }).input;
}

function semanticDraftFromResult(value: unknown): Record<string, unknown> {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    throw new TypeError("expected result object");
  }

  const {
    contract_version: _contractVersion,
    task_id: _taskId,
    provenance: _provenance,
    ...draft
  } = value as Record<string, unknown>;

  return draft;
}

test("TypeScript fingerprint matches canonical TA-002 Python contract fingerprint", async () => {
  const input = await readCaseInput("TA-002");

  assert.equal(
    fingerprintTechnicalArchitectInput(input),
    "sha256:0e53b901edf843755955da772659b47487f09b91f7d205dce1c4769fa39bb017",
  );
});

test("TypeScript fingerprint matches canonical TA-003 Python contract fingerprint", async () => {
  const input = await readCaseInput("TA-003");

  assert.equal(
    fingerprintTechnicalArchitectInput(input),
    "sha256:b5ebfd7352cfca70bc92528146a2d4239fcdfc242c215afe1eabeec176e79d05",
  );
});

test("accepts a valid BLOCKED result as successful invocation", async () => {
  const input = await readCaseInput("TA-003");
  const fullResult = await readJson(
    "evals/m1/result-examples/valid-blocked.json",
  );
  const provider = new FixtureProvider({
    kind: "output",
    value: semanticDraftFromResult(fullResult),
  });

  const outcome = await executeTechnicalArchitect(input, provider);

  assert.equal(outcome.ok, true);
  assert.equal(provider.attempts, 1);

  if (!outcome.ok) {
    return;
  }

  assert.equal(outcome.result.status, "BLOCKED");
  assert.equal(outcome.result.proposal, null);
  assert.equal(
    outcome.result.provenance.input_fingerprint,
    "sha256:b5ebfd7352cfca70bc92528146a2d4239fcdfc242c215afe1eabeec176e79d05",
  );
});

test("accepts a valid COMPLETED result and binds runtime provenance", async () => {
  const input = await readCaseInput("TA-002");
  const fullResult = await readJson(
    "evals/m1/result-examples/valid-completed.json",
  );
  const provider = new FixtureProvider({
    kind: "output",
    value: semanticDraftFromResult(fullResult),
  });

  const outcome = await executeTechnicalArchitect(input, provider);

  assert.equal(outcome.ok, true);
  assert.equal(provider.attempts, 1);

  if (!outcome.ok) {
    return;
  }

  assert.equal(outcome.result.status, "COMPLETED");
  assert.equal(outcome.result.task_id, "TA-002");
  assert.equal(
    outcome.result.provenance.configuration_fingerprint,
    input.resolved_configuration_fingerprint,
  );
});

test("rejects provider attempts to author runtime-owned provenance", async () => {
  const input = await readCaseInput("TA-003");
  const fullResult = await readJson(
    "evals/m1/result-examples/valid-blocked.json",
  );
  const provider = new FixtureProvider({
    kind: "output",
    value: fullResult,
  });

  const outcome = await executeTechnicalArchitect(input, provider);

  assert.equal(outcome.ok, false);
  assert.equal(provider.attempts, 1);

  if (outcome.ok) {
    return;
  }

  assert.equal(outcome.code, "RESULT_CONTRACT_VIOLATION");
  assert.ok(
    outcome.errors.some((error) =>
      error.includes("reserved field"),
    ),
  );
});

test("rejects COMPLETED result with unresolved material blocker", async () => {
  const input = await readCaseInput("TA-003");
  const fullResult = await readJson(
    "evals/m1/result-examples/invalid-completed-with-blocker.json",
  );
  const provider = new FixtureProvider({
    kind: "output",
    value: semanticDraftFromResult(fullResult),
  });

  const outcome = await executeTechnicalArchitect(input, provider);

  assert.equal(outcome.ok, false);
  assert.equal(provider.attempts, 1);

  if (outcome.ok) {
    return;
  }

  assert.equal(outcome.code, "RESULT_CONTRACT_VIOLATION");
  assert.ok(
    outcome.errors.some((error) =>
      error.includes("COMPLETED with unresolved blocking conflict"),
    ),
  );
});

test("invalid input fails before provider invocation", async () => {
  const input = await readCaseInput("TA-003");
  const invalidInput = structuredClone(input) as unknown as {
    capability_boundary: string[];
  };
  invalidInput.capability_boundary.push("WRITE");

  const provider = new FixtureProvider({
    kind: "output",
    value: {},
  });

  const outcome = await executeTechnicalArchitect(invalidInput, provider);

  assert.equal(outcome.ok, false);
  assert.equal(provider.attempts, 0);

  if (outcome.ok) {
    return;
  }

  assert.equal(outcome.code, "INVALID_INPUT");
});

test("provider failure is distinct from BLOCKED agent result", async () => {
  const input = await readCaseInput("TA-003");
  const provider = new FixtureProvider({
    kind: "error",
    error: new Error("fixture provider unavailable"),
  });

  const outcome = await executeTechnicalArchitect(input, provider);

  assert.equal(outcome.ok, false);
  assert.equal(provider.attempts, 1);

  if (outcome.ok) {
    return;
  }

  assert.equal(outcome.code, "PROVIDER_FAILURE");
  assert.equal(outcome.stage, "PROVIDER_INVOCATION");
});
