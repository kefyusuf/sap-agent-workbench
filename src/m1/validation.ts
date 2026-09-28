import {
  INPUT_CONTRACT_VERSION,
  RESULT_CONTRACT_VERSION,
  type CapabilityVerb,
  type TechnicalArchitectInput,
  type TechnicalArchitectResult,
} from "./contracts.js";

const FINGERPRINT = /^sha256:[a-f0-9]{64}$/;
const INPUT_ID_PATTERNS = {
  constraint: /^K-[0-9]{3,}$/,
  claim: /^IC-[0-9]{3,}$/,
  unknown: /^IU-[0-9]{3,}$/,
  conflict: /^IX-[0-9]{3,}$/,
  evidence: /^E-[0-9]{3,}$/,
};
const RESULT_ID_PATTERNS = {
  claim: /^C-[0-9]{3,}$/,
  unknown: /^U-[0-9]{3,}$/,
  conflict: /^X-[0-9]{3,}$/,
  option: /^OPT-[0-9]{3,}$/,
  verification: /^V-[0-9]{3,}$/,
};

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
const CONSTRAINT_AUTHORITIES = new Set([
  "SYSTEM_VERIFIED",
  "PROJECT_APPROVED",
  "ORGANIZATION_APPROVED",
  "OFFICIAL_VENDOR",
  "INTERNAL_REFERENCE",
  "USER_PROVIDED",
]);
const EVIDENCE_TYPES = new Set([
  "LIVE_SYSTEM",
  "SOURCE_CODE",
  "EXECUTION_RESULT",
  "TEST_RESULT",
  "STATIC_ANALYSIS",
  "LOG",
  "CONFIGURATION",
  "APPROVED_DOCUMENT",
  "DECISION_RECORD",
  "OFFICIAL_DOCUMENTATION",
  "USER_CONFIRMATION",
]);
const DISCOVERY_CATEGORIES = new Set([
  "SAP_STANDARD",
  "CONFIGURATION",
  "EXISTING_IMPLEMENTATION",
  "SUPPORTED_EXTENSION",
  "RELEASED_API_EVENT",
  "SIDE_BY_SIDE_EXTENSION",
  "CUSTOM_IMPLEMENTATION",
]);
const DISCOVERY_STATUSES = new Set([
  "APPLICABLE",
  "NOT_APPLICABLE",
  "UNKNOWN",
]);
const OPTION_FAMILIES = new Set([
  "STANDARD_CONFIGURATION",
  "SUPPORTED_EXTENSION",
  "RELEASED_API_EVENT",
  "INTEGRATION",
  "SIDE_BY_SIDE_BTP",
  "CUSTOM_IMPLEMENTATION",
  "OTHER",
]);
const NEXT_ACTIONS = new Set([
  "REQUEST_CLARIFICATION",
  "VERIFY_CONTEXT",
  "REVIEW_ARCHITECTURE",
  "HANDOFF_IMPLEMENTATION",
  "NONE",
]);
const FORBIDDEN_SECRET_KEYS = new Set([
  "password",
  "client_secret",
  "api_key",
  "private_key",
  "access_token",
  "refresh_token",
]);

const INPUT_TOP_LEVEL_KEYS = [
  "contract_version",
  "task",
  "scope",
  "constraints",
  "context",
  "evidence_catalog",
  "capability_boundary",
  "resolved_configuration_fingerprint",
  "requested_result_contract",
] as const;

const RESULT_TOP_LEVEL_KEYS = [
  "contract_version",
  "task_id",
  "provenance",
  "status",
  "requirement_summary",
  "scope",
  "claims",
  "unknowns",
  "conflicts",
  "existing_solution_discovery",
  "solution_options",
  "proposal",
  "required_verification",
  "implementation_handoff",
  "requested_capabilities",
  "next_action",
] as const;

export interface InvocationReferenceContext {
  readonly inputFingerprint: string;
  readonly configurationFingerprint: string;
  readonly evidenceIds: ReadonlySet<string>;
  readonly sourceRefs: ReadonlySet<string>;
}

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

function validateExactKeys(
  value: Record<string, unknown>,
  keys: readonly string[],
  errors: string[],
  path: string,
): void {
  const expected = new Set(keys);

  for (const key of keys) {
    if (!(key in value)) {
      errors.push(`${path}: missing ${key}`);
    }
  }

  for (const key of Object.keys(value)) {
    if (!expected.has(key)) {
      errors.push(`${path}: unknown field ${key}`);
    }
  }
}

function validateStringArray(
  value: unknown,
  errors: string[],
  path: string,
  options?: {
    nonEmptyItems?: boolean;
    unique?: boolean;
  },
): value is string[] {
  if (!isStringArray(value)) {
    errors.push(`${path}: expected string array`);
    return false;
  }

  if (options?.nonEmptyItems) {
    value.forEach((item, index) => {
      if (item.trim().length === 0) {
        errors.push(`${path}[${index}]: must be non-empty`);
      }
    });
  }

  if (options?.unique && new Set(value).size !== value.length) {
    errors.push(`${path}: duplicate values`);
  }

  return true;
}

function validateIds(
  items: unknown,
  pattern: RegExp,
  errors: string[],
  path: string,
): Set<string> {
  const ids = new Set<string>();

  if (!Array.isArray(items)) {
    errors.push(`${path}: expected array`);
    return ids;
  }

  items.forEach((item, index) => {
    if (!isRecord(item) || typeof item.id !== "string" || !pattern.test(item.id)) {
      errors.push(`${path}[${index}].id: invalid`);
      return;
    }

    if (ids.has(item.id)) {
      errors.push(`${path}[${index}].id: duplicate ${item.id}`);
    }
    ids.add(item.id);
  });

  return ids;
}

function validateCrossCollectionIds(
  collections: ReadonlyArray<ReadonlySet<string>>,
  errors: string[],
  path: string,
): void {
  const seen = new Set<string>();

  for (const collection of collections) {
    for (const id of collection) {
      if (seen.has(id)) {
        errors.push(`${path}: duplicate result-local id ${id}`);
      }
      seen.add(id);
    }
  }
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

function validateReferenceSet(
  refs: unknown,
  allowed: ReadonlySet<string> | undefined,
  errors: string[],
  path: string,
): string[] {
  if (!validateStringArray(refs, errors, path, {
    nonEmptyItems: true,
    unique: true,
  })) {
    return [];
  }

  if (allowed) {
    for (const ref of refs) {
      if (!allowed.has(ref)) {
        errors.push(`${path}: unknown reference ${ref}`);
      }
    }
  }

  return refs;
}

export function buildInvocationReferenceContext(
  input: TechnicalArchitectInput,
  inputFingerprint: string,
): InvocationReferenceContext {
  const evidenceIds = new Set(
    input.evidence_catalog.map((evidence) => evidence.id),
  );
  const sourceRefs = new Set<string>();

  for (const constraint of input.constraints) {
    constraint.source_refs.forEach((ref) => sourceRefs.add(ref));
  }

  for (const claim of input.context.claims) {
    claim.source_refs.forEach((ref) => sourceRefs.add(ref));
  }

  for (const conflict of input.context.conflicts) {
    conflict.source_refs.forEach((ref) => sourceRefs.add(ref));
  }

  for (const evidence of input.evidence_catalog) {
    sourceRefs.add(evidence.source_ref);
  }

  return {
    inputFingerprint,
    configurationFingerprint: input.resolved_configuration_fingerprint,
    evidenceIds,
    sourceRefs,
  };
}

export function validateTechnicalArchitectInput(value: unknown): string[] {
  const errors: string[] = [];

  if (!isRecord(value)) {
    return ["$: expected object"];
  }

  validateExactKeys(value, INPUT_TOP_LEVEL_KEYS, errors, "$");

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
    validateExactKeys(
      task,
      ["id", "requirement", "requested_outcome"],
      errors,
      "$.task",
    );

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
    validateExactKeys(
      scope,
      ["modules", "systems", "environments", "project", "landscape"],
      errors,
      "$.scope",
    );
    validateStringArray(scope.modules, errors, "$.scope.modules");
    validateStringArray(scope.systems, errors, "$.scope.systems");
    validateStringArray(scope.environments, errors, "$.scope.environments");

    if (!(scope.project === null || typeof scope.project === "string")) {
      errors.push("$.scope.project: expected string or null");
    }
    if (!(scope.landscape === null || typeof scope.landscape === "string")) {
      errors.push("$.scope.landscape: expected string or null");
    }
  }

  const constraintIds = validateIds(
    value.constraints,
    INPUT_ID_PATTERNS.constraint,
    errors,
    "$.constraints",
  );

  if (Array.isArray(value.constraints)) {
    value.constraints.forEach((constraint, index) => {
      if (!isRecord(constraint)) {
        errors.push(`$.constraints[${index}]: expected object`);
        return;
      }

      validateExactKeys(
        constraint,
        ["id", "statement", "authority", "source_refs"],
        errors,
        `$.constraints[${index}]`,
      );

      if (!hasNonEmptyString(constraint.statement)) {
        errors.push(`$.constraints[${index}].statement: must be non-empty`);
      }
      if (!CONSTRAINT_AUTHORITIES.has(String(constraint.authority))) {
        errors.push(`$.constraints[${index}].authority: invalid`);
      }
      validateStringArray(
        constraint.source_refs,
        errors,
        `$.constraints[${index}].source_refs`,
        { nonEmptyItems: true, unique: true },
      );
    });
  }

  const evidenceIds = validateIds(
    value.evidence_catalog,
    INPUT_ID_PATTERNS.evidence,
    errors,
    "$.evidence_catalog",
  );

  if (Array.isArray(value.evidence_catalog)) {
    value.evidence_catalog.forEach((evidence, index) => {
      if (!isRecord(evidence)) {
        errors.push(`$.evidence_catalog[${index}]: expected object`);
        return;
      }

      validateExactKeys(
        evidence,
        ["id", "type", "source_ref", "revision", "summary"],
        errors,
        `$.evidence_catalog[${index}]`,
      );

      if (!EVIDENCE_TYPES.has(String(evidence.type))) {
        errors.push(`$.evidence_catalog[${index}].type: invalid`);
      }
      if (!hasNonEmptyString(evidence.source_ref)) {
        errors.push(`$.evidence_catalog[${index}].source_ref: invalid`);
      }
      if (!(evidence.revision === null || typeof evidence.revision === "string")) {
        errors.push(`$.evidence_catalog[${index}].revision: expected string or null`);
      }
      if (!hasNonEmptyString(evidence.summary)) {
        errors.push(`$.evidence_catalog[${index}].summary: invalid`);
      }
    });
  }

  const context = value.context;
  let claimIds = new Set<string>();
  let unknownIds = new Set<string>();
  let conflictIds = new Set<string>();

  if (!isRecord(context)) {
    errors.push("$.context: expected object");
  } else {
    validateExactKeys(
      context,
      ["claims", "unknowns", "conflicts"],
      errors,
      "$.context",
    );

    claimIds = validateIds(
      context.claims,
      INPUT_ID_PATTERNS.claim,
      errors,
      "$.context.claims",
    );

    if (Array.isArray(context.claims)) {
      context.claims.forEach((claim, index) => {
        if (!isRecord(claim)) {
          errors.push(`$.context.claims[${index}]: expected object`);
          return;
        }

        validateExactKeys(
          claim,
          [
            "id",
            "classification",
            "statement",
            "system_specific",
            "evidence_refs",
            "source_refs",
          ],
          errors,
          `$.context.claims[${index}]`,
        );

        if (!CLAIM_CLASSES.has(String(claim.classification))) {
          errors.push(`$.context.claims[${index}].classification: invalid`);
        }
        if (!hasNonEmptyString(claim.statement)) {
          errors.push(`$.context.claims[${index}].statement: invalid`);
        }
        if (typeof claim.system_specific !== "boolean") {
          errors.push(`$.context.claims[${index}].system_specific: expected boolean`);
        }

        const evidenceRefs = validateReferenceSet(
          claim.evidence_refs,
          evidenceIds,
          errors,
          `$.context.claims[${index}].evidence_refs`,
        );
        const sourceRefs = validateReferenceSet(
          claim.source_refs,
          undefined,
          errors,
          `$.context.claims[${index}].source_refs`,
        );

        if (claim.classification === "VERIFIED" && evidenceRefs.length === 0) {
          errors.push(`$.context.claims[${index}]: VERIFIED requires evidence`);
        }

        if (
          claim.classification === "KNOWN" &&
          evidenceRefs.length === 0 &&
          sourceRefs.length === 0
        ) {
          errors.push(`$.context.claims[${index}]: KNOWN requires support`);
        }
      });
    }

    unknownIds = validateIds(
      context.unknowns,
      INPUT_ID_PATTERNS.unknown,
      errors,
      "$.context.unknowns",
    );

    if (Array.isArray(context.unknowns)) {
      context.unknowns.forEach((unknownItem, index) => {
        if (!isRecord(unknownItem)) {
          errors.push(`$.context.unknowns[${index}]: expected object`);
          return;
        }

        validateExactKeys(
          unknownItem,
          ["id", "statement", "material", "blocks_decision", "verification"],
          errors,
          `$.context.unknowns[${index}]`,
        );

        if (!hasNonEmptyString(unknownItem.statement)) {
          errors.push(`$.context.unknowns[${index}].statement: invalid`);
        }
        if (typeof unknownItem.material !== "boolean") {
          errors.push(`$.context.unknowns[${index}].material: expected boolean`);
        }
        if (typeof unknownItem.blocks_decision !== "boolean") {
          errors.push(`$.context.unknowns[${index}].blocks_decision: expected boolean`);
        }
        if (!hasNonEmptyString(unknownItem.verification)) {
          errors.push(`$.context.unknowns[${index}].verification: invalid`);
        }
      });
    }

    conflictIds = validateIds(
      context.conflicts,
      INPUT_ID_PATTERNS.conflict,
      errors,
      "$.context.conflicts",
    );

    if (Array.isArray(context.conflicts)) {
      context.conflicts.forEach((conflict, index) => {
        if (!isRecord(conflict)) {
          errors.push(`$.context.conflicts[${index}]: expected object`);
          return;
        }

        validateExactKeys(
          conflict,
          [
            "id",
            "statement",
            "material",
            "blocks_decision",
            "source_refs",
            "verification",
          ],
          errors,
          `$.context.conflicts[${index}]`,
        );

        if (!hasNonEmptyString(conflict.statement)) {
          errors.push(`$.context.conflicts[${index}].statement: invalid`);
        }
        if (typeof conflict.material !== "boolean") {
          errors.push(`$.context.conflicts[${index}].material: expected boolean`);
        }
        if (typeof conflict.blocks_decision !== "boolean") {
          errors.push(`$.context.conflicts[${index}].blocks_decision: expected boolean`);
        }

        const sourceRefs = validateReferenceSet(
          conflict.source_refs,
          undefined,
          errors,
          `$.context.conflicts[${index}].source_refs`,
        );
        if (new Set(sourceRefs).size < 2) {
          errors.push(`$.context.conflicts[${index}]: requires >=2 unique source_refs`);
        }

        if (!hasNonEmptyString(conflict.verification)) {
          errors.push(`$.context.conflicts[${index}].verification: invalid`);
        }
      });
    }
  }

  validateCrossCollectionIds(
    [constraintIds, evidenceIds, claimIds, unknownIds, conflictIds],
    errors,
    "$",
  );

  if (!Array.isArray(value.capability_boundary)) {
    errors.push("$.capability_boundary: expected array");
  } else {
    const capabilities = value.capability_boundary;

    if (new Set(capabilities).size !== capabilities.length) {
      errors.push("$.capability_boundary: duplicate capability");
    }

    capabilities.forEach((capability, index) => {
      if (
        typeof capability !== "string" ||
        !ALLOWED_CAPABILITIES.has(capability as CapabilityVerb)
      ) {
        errors.push(`$.capability_boundary[${index}]: forbidden capability ${String(capability)}`);
      }
    });
  }

  errors.push(...findRawSecrets(value));
  return errors;
}

function validateResultScope(value: unknown, errors: string[]): void {
  if (!isRecord(value)) {
    errors.push("$.scope: expected object");
    return;
  }

  validateExactKeys(
    value,
    ["modules", "systems", "environments", "project"],
    errors,
    "$.scope",
  );
  validateStringArray(value.modules, errors, "$.scope.modules");
  validateStringArray(value.systems, errors, "$.scope.systems");
  validateStringArray(value.environments, errors, "$.scope.environments");

  if (!(value.project === null || typeof value.project === "string")) {
    errors.push("$.scope.project: expected string or null");
  }
}

export function validateTechnicalArchitectResult(
  value: unknown,
  expected?: InvocationReferenceContext,
): string[] {
  const errors: string[] = [];

  if (!isRecord(value)) {
    return ["$: expected object"];
  }

  validateExactKeys(value, RESULT_TOP_LEVEL_KEYS, errors, "$");

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
    validateExactKeys(
      provenance,
      ["input_fingerprint", "configuration_fingerprint"],
      errors,
      "$.provenance",
    );

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

  validateResultScope(value.scope, errors);

  const claimIds = validateIds(
    value.claims,
    RESULT_ID_PATTERNS.claim,
    errors,
    "$.claims",
  );
  const assumedClaimIds = new Set<string>();

  if (Array.isArray(value.claims)) {
    value.claims.forEach((claim, index) => {
      if (!isRecord(claim)) {
        errors.push(`$.claims[${index}]: expected object`);
        return;
      }

      validateExactKeys(
        claim,
        [
          "id",
          "classification",
          "statement",
          "system_specific",
          "evidence_refs",
          "source_refs",
        ],
        errors,
        `$.claims[${index}]`,
      );

      if (!CLAIM_CLASSES.has(String(claim.classification))) {
        errors.push(`$.claims[${index}].classification: invalid`);
      }
      if (claim.classification === "ASSUMED" && typeof claim.id === "string") {
        assumedClaimIds.add(claim.id);
      }
      if (!hasNonEmptyString(claim.statement)) {
        errors.push(`$.claims[${index}].statement: invalid`);
      }
      if (typeof claim.system_specific !== "boolean") {
        errors.push(`$.claims[${index}].system_specific: expected boolean`);
      }

      const evidenceRefs = validateReferenceSet(
        claim.evidence_refs,
        expected?.evidenceIds,
        errors,
        `$.claims[${index}].evidence_refs`,
      );
      const sourceRefs = validateReferenceSet(
        claim.source_refs,
        expected?.sourceRefs,
        errors,
        `$.claims[${index}].source_refs`,
      );

      if (claim.classification === "VERIFIED" && evidenceRefs.length === 0) {
        errors.push(`$.claims[${index}]: VERIFIED requires evidence`);
      }

      if (
        claim.classification === "KNOWN" &&
        evidenceRefs.length === 0 &&
        sourceRefs.length === 0
      ) {
        errors.push(`$.claims[${index}]: KNOWN requires support`);
      }
    });
  }

  const unknownIds = validateIds(
    value.unknowns,
    RESULT_ID_PATTERNS.unknown,
    errors,
    "$.unknowns",
  );
  let blockingUnknown = false;

  if (Array.isArray(value.unknowns)) {
    value.unknowns.forEach((unknownItem, index) => {
      if (!isRecord(unknownItem)) {
        errors.push(`$.unknowns[${index}]: expected object`);
        return;
      }

      validateExactKeys(
        unknownItem,
        ["id", "statement", "material", "blocks_decision", "verification"],
        errors,
        `$.unknowns[${index}]`,
      );

      if (!hasNonEmptyString(unknownItem.statement)) {
        errors.push(`$.unknowns[${index}].statement: invalid`);
      }
      if (typeof unknownItem.material !== "boolean") {
        errors.push(`$.unknowns[${index}].material: expected boolean`);
      }
      if (typeof unknownItem.blocks_decision !== "boolean") {
        errors.push(`$.unknowns[${index}].blocks_decision: expected boolean`);
      }
      if (!hasNonEmptyString(unknownItem.verification)) {
        errors.push(`$.unknowns[${index}].verification: invalid`);
      }

      if (
        unknownItem.material === true &&
        unknownItem.blocks_decision === true
      ) {
        blockingUnknown = true;
      }
    });
  }

  const conflictIds = validateIds(
    value.conflicts,
    RESULT_ID_PATTERNS.conflict,
    errors,
    "$.conflicts",
  );
  let blockingConflict = false;

  if (Array.isArray(value.conflicts)) {
    value.conflicts.forEach((conflict, index) => {
      if (!isRecord(conflict)) {
        errors.push(`$.conflicts[${index}]: expected object`);
        return;
      }

      validateExactKeys(
        conflict,
        [
          "id",
          "statement",
          "material",
          "blocks_decision",
          "status",
          "source_refs",
          "verification",
        ],
        errors,
        `$.conflicts[${index}]`,
      );

      if (!hasNonEmptyString(conflict.statement)) {
        errors.push(`$.conflicts[${index}].statement: invalid`);
      }
      if (typeof conflict.material !== "boolean") {
        errors.push(`$.conflicts[${index}].material: expected boolean`);
      }
      if (typeof conflict.blocks_decision !== "boolean") {
        errors.push(`$.conflicts[${index}].blocks_decision: expected boolean`);
      }
      if (conflict.status !== "UNRESOLVED" && conflict.status !== "RESOLVED") {
        errors.push(`$.conflicts[${index}].status: invalid`);
      }

      const sourceRefs = validateReferenceSet(
        conflict.source_refs,
        expected?.sourceRefs,
        errors,
        `$.conflicts[${index}].source_refs`,
      );
      if (new Set(sourceRefs).size < 2) {
        errors.push(`$.conflicts[${index}]: requires >=2 unique source_refs`);
      }

      if (!hasNonEmptyString(conflict.verification)) {
        errors.push(`$.conflicts[${index}].verification: invalid`);
      }

      if (
        conflict.material === true &&
        conflict.blocks_decision === true &&
        conflict.status === "UNRESOLVED"
      ) {
        blockingConflict = true;
      }
    });
  }

  const discovery = value.existing_solution_discovery;
  let discoveryPerformed = false;

  if (!isRecord(discovery)) {
    errors.push("$.existing_solution_discovery: expected object");
  } else {
    validateExactKeys(
      discovery,
      ["performed", "checks"],
      errors,
      "$.existing_solution_discovery",
    );

    if (typeof discovery.performed !== "boolean") {
      errors.push("$.existing_solution_discovery.performed: expected boolean");
    }
    discoveryPerformed = discovery.performed === true;

    if (!Array.isArray(discovery.checks)) {
      errors.push("$.existing_solution_discovery.checks: expected array");
    } else {
      const categories = new Set<string>();

      discovery.checks.forEach((check, index) => {
        if (!isRecord(check)) {
          errors.push(`$.existing_solution_discovery.checks[${index}]: expected object`);
          return;
        }

        validateExactKeys(
          check,
          ["category", "status", "notes", "evidence_refs"],
          errors,
          `$.existing_solution_discovery.checks[${index}]`,
        );

        if (!DISCOVERY_CATEGORIES.has(String(check.category))) {
          errors.push(`$.existing_solution_discovery.checks[${index}].category: invalid`);
        }

        if (typeof check.category === "string") {
          if (categories.has(check.category)) {
            errors.push(`$.existing_solution_discovery.checks[${index}].category: duplicate ${check.category}`);
          }
          categories.add(check.category);
        }

        if (!DISCOVERY_STATUSES.has(String(check.status))) {
          errors.push(`$.existing_solution_discovery.checks[${index}].status: invalid`);
        }
        if (typeof check.notes !== "string") {
          errors.push(`$.existing_solution_discovery.checks[${index}].notes: expected string`);
        }

        validateReferenceSet(
          check.evidence_refs,
          expected?.evidenceIds,
          errors,
          `$.existing_solution_discovery.checks[${index}].evidence_refs`,
        );
      });
    }
  }

  const optionIds = validateIds(
    value.solution_options,
    RESULT_ID_PATTERNS.option,
    errors,
    "$.solution_options",
  );

  if (Array.isArray(value.solution_options)) {
    value.solution_options.forEach((option, index) => {
      if (!isRecord(option)) {
        errors.push(`$.solution_options[${index}]: expected object`);
        return;
      }

      validateExactKeys(
        option,
        [
          "id",
          "title",
          "family",
          "description",
          "tradeoffs",
          "risks",
          "evidence_refs",
          "assumption_refs",
          "required_verification",
        ],
        errors,
        `$.solution_options[${index}]`,
      );

      if (!hasNonEmptyString(option.title)) {
        errors.push(`$.solution_options[${index}].title: invalid`);
      }
      if (!OPTION_FAMILIES.has(String(option.family))) {
        errors.push(`$.solution_options[${index}].family: invalid`);
      }
      if (!hasNonEmptyString(option.description)) {
        errors.push(`$.solution_options[${index}].description: invalid`);
      }

      validateStringArray(
        option.tradeoffs,
        errors,
        `$.solution_options[${index}].tradeoffs`,
      );
      validateStringArray(
        option.risks,
        errors,
        `$.solution_options[${index}].risks`,
      );
      validateReferenceSet(
        option.evidence_refs,
        expected?.evidenceIds,
        errors,
        `$.solution_options[${index}].evidence_refs`,
      );
      const assumptionRefs = validateReferenceSet(
        option.assumption_refs,
        assumedClaimIds,
        errors,
        `$.solution_options[${index}].assumption_refs`,
      );
      void assumptionRefs;
      validateStringArray(
        option.required_verification,
        errors,
        `$.solution_options[${index}].required_verification`,
      );
    });
  }

  const verificationIds = validateIds(
    value.required_verification,
    RESULT_ID_PATTERNS.verification,
    errors,
    "$.required_verification",
  );
  let blockingVerification = false;

  if (Array.isArray(value.required_verification)) {
    value.required_verification.forEach((verification, index) => {
      if (!isRecord(verification)) {
        errors.push(`$.required_verification[${index}]: expected object`);
        return;
      }

      validateExactKeys(
        verification,
        ["id", "description", "why", "blocking"],
        errors,
        `$.required_verification[${index}]`,
      );

      if (!hasNonEmptyString(verification.description)) {
        errors.push(`$.required_verification[${index}].description: invalid`);
      }
      if (!hasNonEmptyString(verification.why)) {
        errors.push(`$.required_verification[${index}].why: invalid`);
      }
      if (typeof verification.blocking !== "boolean") {
        errors.push(`$.required_verification[${index}].blocking: expected boolean`);
      }
      if (verification.blocking === true) {
        blockingVerification = true;
      }
    });
  }

  validateCrossCollectionIds(
    [claimIds, unknownIds, conflictIds, optionIds, verificationIds],
    errors,
    "$",
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
    validateExactKeys(
      value.proposal,
      [
        "selected_option_id",
        "summary",
        "rationale",
        "confidence",
        "evidence_refs",
        "assumption_refs",
      ],
      errors,
      "$.proposal",
    );

    if (
      typeof value.proposal.selected_option_id !== "string" ||
      !optionIds.has(value.proposal.selected_option_id)
    ) {
      errors.push("$.proposal.selected_option_id: unknown option");
    }
    if (!hasNonEmptyString(value.proposal.summary)) {
      errors.push("$.proposal.summary: invalid");
    }
    validateStringArray(value.proposal.rationale, errors, "$.proposal.rationale");

    if (
      value.proposal.confidence !== "LOW" &&
      value.proposal.confidence !== "MEDIUM" &&
      value.proposal.confidence !== "HIGH"
    ) {
      errors.push("$.proposal.confidence: invalid");
    }

    validateReferenceSet(
      value.proposal.evidence_refs,
      expected?.evidenceIds,
      errors,
      "$.proposal.evidence_refs",
    );
    validateReferenceSet(
      value.proposal.assumption_refs,
      assumedClaimIds,
      errors,
      "$.proposal.assumption_refs",
    );

    if (!discoveryPerformed) {
      errors.push("$.proposal: discovery must be performed");
    }
  }

  const handoff = value.implementation_handoff;
  if (!isRecord(handoff)) {
    errors.push("$.implementation_handoff: expected object");
  } else {
    validateExactKeys(
      handoff,
      ["ready", "notes"],
      errors,
      "$.implementation_handoff",
    );

    if (typeof handoff.ready !== "boolean") {
      errors.push("$.implementation_handoff.ready: expected boolean");
    }
    validateStringArray(handoff.notes, errors, "$.implementation_handoff.notes");

    if (value.status !== "COMPLETED" && handoff.ready !== false) {
      errors.push("$.implementation_handoff.ready: non-COMPLETED must be false");
    }
  }

  if (!Array.isArray(value.requested_capabilities)) {
    errors.push("$.requested_capabilities: expected array");
  } else {
    value.requested_capabilities.forEach((request, index) => {
      if (!isRecord(request)) {
        errors.push(`$.requested_capabilities[${index}]: expected object`);
        return;
      }

      validateExactKeys(
        request,
        ["verb", "purpose"],
        errors,
        `$.requested_capabilities[${index}]`,
      );

      if (
        typeof request.verb !== "string" ||
        !ALLOWED_CAPABILITIES.has(request.verb as CapabilityVerb)
      ) {
        errors.push(`$.requested_capabilities[${index}].verb: forbidden ${String(request.verb)}`);
      }
      if (!hasNonEmptyString(request.purpose)) {
        errors.push(`$.requested_capabilities[${index}].purpose: invalid`);
      }
    });
  }

  const nextAction = value.next_action;
  if (!isRecord(nextAction)) {
    errors.push("$.next_action: expected object");
  } else {
    validateExactKeys(
      nextAction,
      ["type", "description"],
      errors,
      "$.next_action",
    );

    if (!NEXT_ACTIONS.has(String(nextAction.type))) {
      errors.push("$.next_action.type: invalid");
    }
    if (typeof nextAction.description !== "string") {
      errors.push("$.next_action.description: expected string");
    }

    if (
      value.status !== "COMPLETED" &&
      nextAction.type === "HANDOFF_IMPLEMENTATION"
    ) {
      errors.push("$.next_action: non-COMPLETED cannot hand off implementation");
    }
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
