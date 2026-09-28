import {
  RESULT_CONTRACT_VERSION,
  type ExecutionMetadata,
  type ExecutionOutcome,
  type TechnicalArchitectDraft,
  type TechnicalArchitectInput,
  type TechnicalArchitectResult,
} from "./contracts.js";
import { fingerprintTechnicalArchitectInput } from "./fingerprint.js";
import type { ProviderAdapter } from "./provider-adapter.js";
import {
  asTechnicalArchitectInput,
  asTechnicalArchitectResult,
  buildInvocationReferenceContext,
  validateTechnicalArchitectInput,
  validateTechnicalArchitectResult,
} from "./validation.js";

const RESERVED_PROVIDER_FIELDS = new Set([
  "contract_version",
  "task_id",
  "provenance",
]);

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function deepFreeze<T>(value: T): Readonly<T> {
  if (value === null || typeof value !== "object" || Object.isFrozen(value)) {
    return value;
  }

  Object.freeze(value);

  if (Array.isArray(value)) {
    for (const nested of value) {
      deepFreeze(nested);
    }
    return value;
  }

  for (const nested of Object.values(value as object)) {
    deepFreeze(nested);
  }

  return value;
}

function executionMetadata(
  adapter: ProviderAdapter | null,
  attempts: number,
  inputFingerprint: string | null,
  configurationFingerprint: string | null,
): ExecutionMetadata {
  return {
    adapter_id: adapter?.id ?? "unavailable",
    adapter_version: adapter?.version ?? "unavailable",
    attempts,
    input_fingerprint: inputFingerprint,
    configuration_fingerprint: configurationFingerprint,
  };
}

function parseProviderOutput(raw: unknown):
  | { ok: true; value: Record<string, unknown> }
  | { ok: false; message: string } {
  let parsed = raw;

  if (typeof raw === "string") {
    try {
      parsed = JSON.parse(raw) as unknown;
    } catch {
      return { ok: false, message: "provider output is not valid JSON" };
    }
  }

  if (!isRecord(parsed)) {
    return { ok: false, message: "provider output must be a JSON object" };
  }

  return { ok: true, value: parsed };
}

function hasReservedProviderField(
  draft: Record<string, unknown>,
): string | null {
  for (const field of RESERVED_PROVIDER_FIELDS) {
    if (field in draft) {
      return field;
    }
  }

  return null;
}

export async function executeTechnicalArchitect(
  inputValue: unknown,
  adapter: ProviderAdapter | null,
): Promise<ExecutionOutcome> {
  const inputErrors = validateTechnicalArchitectInput(inputValue);

  if (inputErrors.length > 0) {
    return {
      ok: false,
      code: "INVALID_INPUT",
      stage: "INPUT_VALIDATION",
      message: "Technical Architect input contract validation failed.",
      errors: inputErrors,
      execution: executionMetadata(adapter, 0, null, null),
    };
  }

  const input = asTechnicalArchitectInput(inputValue);
  const inputFingerprint = fingerprintTechnicalArchitectInput(input);
  const configurationFingerprint = input.resolved_configuration_fingerprint;

  if (adapter === null) {
    return {
      ok: false,
      code: "ADAPTER_UNAVAILABLE",
      stage: "PROVIDER_INVOCATION",
      message: "No provider adapter is available for this invocation.",
      errors: [],
      execution: executionMetadata(
        null,
        0,
        inputFingerprint,
        configurationFingerprint,
      ),
    };
  }

  const immutableInput = deepFreeze(structuredClone(input));

  let raw: unknown;
  try {
    raw = await adapter.invoke(immutableInput);
  } catch (error) {
    return {
      ok: false,
      code: "PROVIDER_FAILURE",
      stage: "PROVIDER_INVOCATION",
      message:
        error instanceof Error
          ? error.message
          : "Provider adapter invocation failed.",
      errors: [],
      execution: executionMetadata(
        adapter,
        1,
        inputFingerprint,
        configurationFingerprint,
      ),
    };
  }

  const parsed = parseProviderOutput(raw);
  if (!parsed.ok) {
    return {
      ok: false,
      code: "MALFORMED_PROVIDER_OUTPUT",
      stage: "OUTPUT_PARSE",
      message: parsed.message,
      errors: [],
      execution: executionMetadata(
        adapter,
        1,
        inputFingerprint,
        configurationFingerprint,
      ),
    };
  }

  const reservedField = hasReservedProviderField(parsed.value);
  if (reservedField !== null) {
    return {
      ok: false,
      code: "RESULT_CONTRACT_VIOLATION",
      stage: "RESULT_VALIDATION",
      message: "Provider draft attempted to set a runtime-owned field.",
      errors: [`provider draft contains reserved field: ${reservedField}`],
      execution: executionMetadata(
        adapter,
        1,
        inputFingerprint,
        configurationFingerprint,
      ),
    };
  }

  const draft = parsed.value as unknown as TechnicalArchitectDraft;
  const normalized: TechnicalArchitectResult = {
    contract_version: RESULT_CONTRACT_VERSION,
    task_id: input.task.id,
    provenance: {
      input_fingerprint: inputFingerprint,
      configuration_fingerprint: configurationFingerprint,
    },
    ...draft,
  };

  const referenceContext = buildInvocationReferenceContext(
    input,
    inputFingerprint,
  );
  const resultErrors = validateTechnicalArchitectResult(
    normalized,
    referenceContext,
  );

  if (resultErrors.length > 0) {
    return {
      ok: false,
      code: "RESULT_CONTRACT_VIOLATION",
      stage: "RESULT_VALIDATION",
      message: "Normalized Technical Architect result failed validation.",
      errors: resultErrors,
      execution: executionMetadata(
        adapter,
        1,
        inputFingerprint,
        configurationFingerprint,
      ),
    };
  }

  return {
    ok: true,
    result: asTechnicalArchitectResult(normalized),
    execution: executionMetadata(
      adapter,
      1,
      inputFingerprint,
      configurationFingerprint,
    ),
  };
}
