import {
  INPUT_CONTRACT_VERSION,
  RESULT_CONTRACT_VERSION,
  type CapabilityVerb,
  type TechnicalArchitectInput,
  type TechnicalArchitectResult,
} from "./contracts.js";

const FINGERPRINT = /^sha256:[a-f0-9]{64}$/;
const ALLOWED_CAPABILITIES = new Set<CapabilityVerb>([
  "READ",
  "QUERY",
  "ANALYZE",
  "PROPOSE",
]);
const CLAIM_CLASSES = new Set([
  "VERIFIED",
  "KNOWN",
  "INFERRED",
  "ASSUMED",
]);
const RESULT_STATUSES = new Set([
  "COMPLETED",
  "NEEDS_CLARIFICATION",
  "BLOCKED",
]);
const FORBIDDEN_SECRET_KEYS = new Set([
  "password",
  "client_secret",
  "api_key",
  "private_key",
  "access_token",
  "refresh_token",
]);

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === "string");
}

function hasNonEmptyString(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

function hasFingerprint(value: unknown): value is string {
  return typeof value === "string" && FINGERPRINT.test(value);
}

function duplicateValues(values: string[]): string[] {
  const seen = new Set<string>();
  const duplicates = new Set<string>();

  for (const value of values) {
    if (seen.has(value)) {
      duplicates.add(value);
    }
    seen.add(value);
  }

  return [...duplicates];
}

function findRawSecrets(value: unknown, path = "$"): string[] {
  const errors: string[] = [];

  if (Array.isArray(value)) {
    value.forEach((item, index) => {
      errors.push(...findRawSecrets(item, `${path}[${index}]`));
    });
    return errors;
  }

  if (!isRecord(value)) {
    return errors;
  }

  for (const [key, nested] of Object.entries(value)) {
    const childPath = `${path}.${key}`;
    if (
      FORBIDDEN_SECRET_KEYS.has(key.toLowerCase()) &&
      nested !== null &&
      nested !== ""
    ) {
      errors.push(`${childPath}: raw secret material forbidden`);
    }
    errors.push(...findRawSecrets(nested, childPath));
  }

  return errors;
}

export function validateTechnicalArchitectInput(value: unknown): string[] {
  const errors: string[] = [];

  if (!isRecord(value)) {
    return ["$: expected object"];
  }

  if (value.contract_version !== INPUT_CONTRACT_VERSION) {
    errors.push("$.contract_version: unsupported");
  }

  if (value.requested_result_contract !== RESULT_CONTRACT_VERSION) {
    errors.push("$.requested_result_contract: unsupported");
  }

  if (!hasFingerprint(value.resolved_configuration_fingerprint)) {
    errors.push("$.resolved_configuration_fingerprint: invalid");
  }

  const task = value.task;
  if (!isRecord(task)) {
    errors.push("$.task: expected object");
  } else {
    if (!hasNonEmptyString(task.id)) {
      errors.push("$.task.id: must be non-empty");
    }
    if (!hasNonEmptyString(task.requirement)) {
      errors.push("$.task.requirement: must be non-empty");
    }
    if (task.requested_outcome !== "ARCHITECTURE_ASSESSMENT") {
      errors.push("$.task.requested_outcome: unsupported");
    }
  }

  const scope = value.scope;
  if (!isRecord(scope)) {
    errors.push("$.scope: expected object");
  } else {
    if (!isStringArray(scope.modules)) {
      errors.push("$.scope.modules: expected string array");
    }
    if (!isStringArray(scope.systems)) {
      errors.push("$.scope.systems: expected string array");
    }
    if (!isStringArray(scope.environments)) {
      errors.push("$.scope.environments: expected string array");
    }
    if (!(scope.project === null || typeof scope.project === "string")) {
      errors.push("$.scope.project: expected string or null");
    }
    if (!(scope.landscape === null || typeof scope.landscape === "string")) {
      errors.push("$.scope.landscape: expected string or null");
    }
  }

  const evidenceCatalog = value.evidence_catalog;
  const evidenceIds = new Set<string>();

  if (!Array.isArray(evidenceCatalog)) {
    errors.push("$.evidence_catalog: expected array");
  } else {
    for (const [index, evidence] of evidenceCatalog.entries()) {
      if (!isRecord(evidence) || !hasNonEmptyString(evidence.id)) {
        errors.push(`$.evidence_catalog[${index}].id: invalid`);
        continue;
      }

      if (evidenceIds.has(evidence.id)) {
        errors.push(`$.evidence_catalog[${index}].id: duplicate ${evidence.id}`);
      }
      evidenceIds.add(evidence.id);

      if (!hasNonEmptyString(evidence.source_ref)) {
        errors.push(`$.evidence_catalog[${index}].source_ref: invalid`);
      }
      if (!hasNonEmptyString(evidence.summary)) {
        errors.push(`$.evidence_catalog[${index}].summary: invalid`);
      }
    }
  }

  const context = value.context;
  if (!isRecord(context)) {
    errors.push("$.context: expected object");
  } else {
    const claims = context.claims;
    if (!Array.isArray(claims)) {
      errors.push("$.context.claims: expected array");
    } else {
      const ids: string[] = [];

      for (const [index, claim] of claims.entries()) {
        if (!isRecord(claim) || !hasNonEmptyString(claim.id)) {
          errors.push(`$.context.claims[${index}].id: invalid`);
          continue;
        }
        ids.push(claim.id);

        if (!CLAIM_CLASSES.has(String(claim.classification))) {
          errors.push(`$.context.claims[${index}].classification: invalid`);
        }
        if (!hasNonEmptyString(claim.statement)) {
          errors.push(`$.context.claims[${index}].statement: invalid`);
        }
        if (typeof claim.system_specific !== "boolean") {
          errors.push(`$.context.claims[${index}].system_specific: expected boolean`);
        }

        const evidenceRefs = claim.evidence_refs;
        const sourceRefs = claim.source_refs;
        if (!isStringArray(evidenceRefs)) {
          errors.push(`$.context.claims[${index}].evidence_refs: expected string array`);
        }
        if (!isStringArray(sourceRefs)) {
          errors.push(`$.context.claims[${index}].source_refs: expected string array`);
        }

        if (isStringArray(evidenceRefs)) {
          for (const ref of evidenceRefs) {
            if (!evidenceIds.has(ref)) {
              errors.push(`$.context.claims[${index}].evidence_refs: unknown ${ref}`);
            }
          }

          if (claim.classification === "VERIFIED" && evidenceRefs.length === 0) {
            errors.push(`$.context.claims[${index}]: VERIFIED requires evidence`);
          }
        }

        if (
          claim.classification === "KNOWN" &&
          isStringArray(evidenceRefs) &&
          isStringArray(sourceRefs) &&
          evidenceRefs.length === 0 &&
          sourceRefs.length === 0
        ) {
          errors.push(`$.context.claims[${index}]: KNOWN requires support`);
        }
      }

      for (const duplicate of duplicateValues(ids)) {
        errors.push(`$.context.claims: duplicate id ${duplicate}`);
      }
    }

    if (!Array.isArray(context.unknowns)) {
      errors.push("$.context.unknowns: expected array");
    }

    if (!Array.isArray(context.conflicts)) {
      errors.push("$.context.conflicts: expected array");
    } else {
      for (const [index, conflict] of context.conflicts.entries()) {
        if (!isRecord(conflict)) {
          errors.push(`$.context.conflicts[${index}]: expected object`);
          continue;
        }

        if (!isStringArray(conflict.source_refs) || new Set(conflict.source_refs).size < 2) {
          errors.push(`$.context.conflicts[${index}]: requires >=2 unique source_refs`);
        }
      }
    }
  }

  const capabilities = value.capability_boundary;
  if (!Array.isArray(capabilities)) {
    errors.push("$.capability_boundary: expected array");
  } else {
    const strings = capabilities.filter(
      (item): item is string => typeof item === "string",
    );

    if (strings.length !== capabilities.length) {
      errors.push("$.capability_boundary: expected string array");
    }

    for (const [index, capability] of strings.entries()) {
      if (!ALLOWED_CAPABILITIES.has(capability as CapabilityVerb)) {
        errors.push(`$.capability_boundary[${index}]: forbidden ${capability}`);
      }
    }

    for (const duplicate of duplicateValues(strings)) {
      errors.push(`$.capability_boundary: duplicate ${duplicate}`);
    }
  }

  errors.push(...findRawSecrets(value));
  return errors;
}

export function validateTechnicalArchitectResult(
  value: unknown,
  expected?: {
    inputFingerprint: string;
    configurationFingerprint: string;
  },
): string[] {
  const errors: string[] = [];

  if (!isRecord(value)) {
    return ["$: expected object"];
  }

  if (value.contract_version !== RESULT_CONTRACT_VERSION) {
    errors.push("$.contract_version: unsupported");
  }

  if (!hasNonEmptyString(value.task_id)) {
    errors.push("$.task_id: invalid");
  }

  const provenance = value.provenance;
  if (!isRecord(provenance)) {
    errors.push("$.provenance: expected object");
  } else {
    if (!hasFingerprint(provenance.input_fingerprint)) {
      errors.push("$.provenance.input_fingerprint: invalid");
    }
    if (!hasFingerprint(provenance.configuration_fingerprint)) {
      errors.push("$.provenance.configuration_fingerprint: invalid");
    }

    if (
      expected &&
      provenance.input_fingerprint !== expected.inputFingerprint
    ) {
      errors.push("$.provenance.input_fingerprint: mismatch");
    }
    if (
      expected &&
      provenance.configuration_fingerprint !==
        expected.configurationFingerprint
    ) {
      errors.push("$.provenance.configuration_fingerprint: mismatch");
    }
  }

  if (!RESULT_STATUSES.has(String(value.status))) {
    errors.push("$.status: invalid");
  }

  if (!hasNonEmptyString(value.requirement_summary)) {
    errors.push("$.requirement_summary: invalid");
  }

  const claims = Array.isArray(value.claims) ? value.claims : [];
  if (!Array.isArray(value.claims)) {
    errors.push("$.claims: expected array");
  }

  const claimIds = new Set<string>();
  for (const [index, claim] of claims.entries()) {
    if (!isRecord(claim) || !hasNonEmptyString(claim.id)) {
      errors.push(`$.claims[${index}].id: invalid`);
      continue;
    }

    if (claimIds.has(claim.id)) {
      errors.push(`$.claims[${index}].id: duplicate ${claim.id}`);
    }
    claimIds.add(claim.id);

    if (!CLAIM_CLASSES.has(String(claim.classification))) {
      errors.push(`$.claims[${index}].classification: invalid`);
    }

    const evidenceRefs = claim.evidence_refs;
    const sourceRefs = claim.source_refs;

    if (!isStringArray(evidenceRefs)) {
      errors.push(`$.claims[${index}].evidence_refs: expected string array`);
    }
    if (!isStringArray(sourceRefs)) {
      errors.push(`$.claims[${index}].source_refs: expected string array`);
    }

    if (
      claim.classification === "VERIFIED" &&
      isStringArray(evidenceRefs) &&
      evidenceRefs.length === 0
    ) {
      errors.push(`$.claims[${index}]: VERIFIED requires evidence`);
    }

    if (
      claim.classification === "KNOWN" &&
      isStringArray(evidenceRefs) &&
      isStringArray(sourceRefs) &&
      evidenceRefs.length === 0 &&
      sourceRefs.length === 0
    ) {
      errors.push(`$.claims[${index}]: KNOWN requires support`);
    }
  }

  const unknowns = Array.isArray(value.unknowns) ? value.unknowns : [];
  if (!Array.isArray(value.unknowns)) {
    errors.push("$.unknowns: expected array");
  }
  const blockingUnknown = unknowns.some(
    (item) =>
      isRecord(item) &&
      item.material === true &&
      item.blocks_decision === true,
  );

  const conflicts = Array.isArray(value.conflicts) ? value.conflicts : [];
  if (!Array.isArray(value.conflicts)) {
    errors.push("$.conflicts: expected array");
  }
  const blockingConflict = conflicts.some(
    (item) =>
      isRecord(item) &&
      item.material === true &&
      item.blocks_decision === true &&
      item.status === "UNRESOLVED",
  );

  const verification = Array.isArray(value.required_verification)
    ? value.required_verification
    : [];
  if (!Array.isArray(value.required_verification)) {
    errors.push("$.required_verification: expected array");
  }
  const blockingVerification = verification.some(
    (item) => isRecord(item) && item.blocking === true,
  );

  const discovery = value.existing_solution_discovery;
  const discoveryPerformed =
    isRecord(discovery) && discovery.performed === true;

  const options = Array.isArray(value.solution_options)
    ? value.solution_options
    : [];
  if (!Array.isArray(value.solution_options)) {
    errors.push("$.solution_options: expected array");
  }
  const optionIds = new Set(
    options
      .filter(isRecord)
      .map((option) => option.id)
      .filter((id): id is string => typeof id === "string"),
  );

  if (value.status === "COMPLETED") {
    if (blockingUnknown) {
      errors.push("$.status: COMPLETED with blocking unknown");
    }
    if (blockingConflict) {
      errors.push("$.status: COMPLETED with unresolved blocking conflict");
    }
    if (blockingVerification) {
      errors.push("$.status: COMPLETED with blocking verification");
    }
    if (!isRecord(value.proposal)) {
      errors.push("$.proposal: COMPLETED requires proposal");
    }
  } else if (value.proposal !== null) {
    errors.push("$.proposal: non-COMPLETED requires null proposal");
  }

  if (isRecord(value.proposal)) {
    if (
      typeof value.proposal.selected_option_id !== "string" ||
      !optionIds.has(value.proposal.selected_option_id)
    ) {
      errors.push("$.proposal.selected_option_id: unknown option");
    }
    if (!discoveryPerformed) {
      errors.push("$.proposal: discovery must be performed");
    }
  }

  const handoff = value.implementation_handoff;
  if (!isRecord(handoff)) {
    errors.push("$.implementation_handoff: expected object");
  } else if (value.status !== "COMPLETED" && handoff.ready !== false) {
    errors.push("$.implementation_handoff.ready: non-COMPLETED must be false");
  }

  const capabilityRequests = value.requested_capabilities;
  if (!Array.isArray(capabilityRequests)) {
    errors.push("$.requested_capabilities: expected array");
  } else {
    for (const [index, request] of capabilityRequests.entries()) {
      if (!isRecord(request) || typeof request.verb !== "string") {
        errors.push(`$.requested_capabilities[${index}]: invalid`);
        continue;
      }
      if (!ALLOWED_CAPABILITIES.has(request.verb as CapabilityVerb)) {
        errors.push(
          `$.requested_capabilities[${index}].verb: forbidden ${request.verb}`,
        );
      }
    }
  }

  const nextAction = value.next_action;
  if (!isRecord(nextAction) || typeof nextAction.type !== "string") {
    errors.push("$.next_action: invalid");
  } else if (
    value.status !== "COMPLETED" &&
    nextAction.type === "HANDOFF_IMPLEMENTATION"
  ) {
    errors.push("$.next_action: non-COMPLETED cannot hand off implementation");
  }

  return errors;
}

export function asTechnicalArchitectInput(
  value: unknown,
): TechnicalArchitectInput {
  return value as TechnicalArchitectInput;
}

export function asTechnicalArchitectResult(
  value: unknown,
): TechnicalArchitectResult {
  return value as TechnicalArchitectResult;
}
