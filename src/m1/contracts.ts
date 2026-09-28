export const INPUT_CONTRACT_VERSION = "m1.technical-architect-input.v1" as const;
export const RESULT_CONTRACT_VERSION = "m1.technical-architect-result.v1" as const;

export type ClaimClassification = "VERIFIED" | "KNOWN" | "INFERRED" | "ASSUMED";
export type CapabilityVerb = "READ" | "QUERY" | "ANALYZE" | "PROPOSE";
export type ResultStatus = "COMPLETED" | "NEEDS_CLARIFICATION" | "BLOCKED";

export interface InputClaim {
  id: string;
  classification: ClaimClassification;
  statement: string;
  system_specific: boolean;
  evidence_refs: string[];
  source_refs: string[];
}

export interface InputUnknown {
  id: string;
  statement: string;
  material: boolean;
  blocks_decision: boolean;
  verification: string;
}

export interface InputConflict {
  id: string;
  statement: string;
  material: boolean;
  blocks_decision: boolean;
  source_refs: string[];
  verification: string;
}

export interface InputConstraint {
  id: string;
  statement: string;
  authority:
    | "SYSTEM_VERIFIED"
    | "PROJECT_APPROVED"
    | "ORGANIZATION_APPROVED"
    | "OFFICIAL_VENDOR"
    | "INTERNAL_REFERENCE"
    | "USER_PROVIDED";
  source_refs: string[];
}

export interface EvidenceRecord {
  id: string;
  type:
    | "LIVE_SYSTEM"
    | "SOURCE_CODE"
    | "EXECUTION_RESULT"
    | "TEST_RESULT"
    | "STATIC_ANALYSIS"
    | "LOG"
    | "CONFIGURATION"
    | "APPROVED_DOCUMENT"
    | "DECISION_RECORD"
    | "OFFICIAL_DOCUMENTATION"
    | "USER_CONFIRMATION";
  source_ref: string;
  revision: string | null;
  summary: string;
}

export interface TechnicalArchitectInput {
  contract_version: typeof INPUT_CONTRACT_VERSION;
  task: {
    id: string;
    requirement: string;
    requested_outcome: "ARCHITECTURE_ASSESSMENT";
  };
  scope: {
    modules: string[];
    systems: string[];
    environments: string[];
    project: string | null;
    landscape: string | null;
  };
  constraints: InputConstraint[];
  context: {
    claims: InputClaim[];
    unknowns: InputUnknown[];
    conflicts: InputConflict[];
  };
  evidence_catalog: EvidenceRecord[];
  capability_boundary: CapabilityVerb[];
  resolved_configuration_fingerprint: string;
  requested_result_contract: typeof RESULT_CONTRACT_VERSION;
}

export interface ResultClaim {
  id: string;
  classification: ClaimClassification;
  statement: string;
  system_specific: boolean;
  evidence_refs: string[];
  source_refs: string[];
}

export interface ResultUnknown {
  id: string;
  statement: string;
  material: boolean;
  blocks_decision: boolean;
  verification: string;
}

export interface ResultConflict {
  id: string;
  statement: string;
  material: boolean;
  blocks_decision: boolean;
  status: "UNRESOLVED" | "RESOLVED";
  source_refs: string[];
  verification: string;
}

export interface DiscoveryCheck {
  category:
    | "SAP_STANDARD"
    | "CONFIGURATION"
    | "EXISTING_IMPLEMENTATION"
    | "SUPPORTED_EXTENSION"
    | "RELEASED_API_EVENT"
    | "SIDE_BY_SIDE_EXTENSION"
    | "CUSTOM_IMPLEMENTATION";
  status: "APPLICABLE" | "NOT_APPLICABLE" | "UNKNOWN";
  notes: string;
  evidence_refs: string[];
}

export interface SolutionOption {
  id: string;
  title: string;
  family:
    | "STANDARD_CONFIGURATION"
    | "SUPPORTED_EXTENSION"
    | "RELEASED_API_EVENT"
    | "INTEGRATION"
    | "SIDE_BY_SIDE_BTP"
    | "CUSTOM_IMPLEMENTATION"
    | "OTHER";
  description: string;
  tradeoffs: string[];
  risks: string[];
  evidence_refs: string[];
  assumption_refs: string[];
  required_verification: string[];
}

export interface Proposal {
  selected_option_id: string;
  summary: string;
  rationale: string[];
  confidence: "LOW" | "MEDIUM" | "HIGH";
  evidence_refs: string[];
  assumption_refs: string[];
}

export interface VerificationItem {
  id: string;
  description: string;
  why: string;
  blocking: boolean;
}

export interface CapabilityRequest {
  verb: CapabilityVerb;
  purpose: string;
}

export interface TechnicalArchitectDraft {
  status: ResultStatus;
  requirement_summary: string;
  scope: {
    modules: string[];
    systems: string[];
    environments: string[];
    project: string | null;
  };
  claims: ResultClaim[];
  unknowns: ResultUnknown[];
  conflicts: ResultConflict[];
  existing_solution_discovery: {
    performed: boolean;
    checks: DiscoveryCheck[];
  };
  solution_options: SolutionOption[];
  proposal: Proposal | null;
  required_verification: VerificationItem[];
  implementation_handoff: {
    ready: boolean;
    notes: string[];
  };
  requested_capabilities: CapabilityRequest[];
  next_action: {
    type:
      | "REQUEST_CLARIFICATION"
      | "VERIFY_CONTEXT"
      | "REVIEW_ARCHITECTURE"
      | "HANDOFF_IMPLEMENTATION"
      | "NONE";
    description: string;
  };
}

export interface TechnicalArchitectResult extends TechnicalArchitectDraft {
  contract_version: typeof RESULT_CONTRACT_VERSION;
  task_id: string;
  provenance: {
    input_fingerprint: string;
    configuration_fingerprint: string;
  };
}

export type ExecutionFailureCode =
  | "INVALID_INPUT"
  | "ADAPTER_UNAVAILABLE"
  | "PROVIDER_FAILURE"
  | "MALFORMED_PROVIDER_OUTPUT"
  | "RESULT_CONTRACT_VIOLATION"
  | "EVALUATION_REJECTED";

export interface ExecutionMetadata {
  adapter_id: string;
  adapter_version: string;
  attempts: number;
  input_fingerprint: string | null;
  configuration_fingerprint: string | null;
}

export type ExecutionOutcome =
  | {
      ok: true;
      result: TechnicalArchitectResult;
      execution: ExecutionMetadata;
    }
  | {
      ok: false;
      code: ExecutionFailureCode;
      stage:
        | "INPUT_VALIDATION"
        | "PROVIDER_INVOCATION"
        | "OUTPUT_PARSE"
        | "RESULT_VALIDATION"
        | "EVALUATION";
      message: string;
      errors: string[];
      execution: ExecutionMetadata;
    };
