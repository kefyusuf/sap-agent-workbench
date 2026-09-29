import type { TechnicalArchitectInput } from "./contracts.js";
import type { ProviderAdapter } from "./provider-adapter.js";

const OPENAI_RESPONSES_ENDPOINT = "https://api.openai.com/v1/responses";
const OPENAI_PROVIDER_ID = "openai-responses";
const OPENAI_PROVIDER_VERSION = "1";

const DRAFT_SCHEMA = {
  type: "object",
  additionalProperties: false,
  required: [
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
  ],
  properties: {
    status: {
      enum: ["COMPLETED", "NEEDS_CLARIFICATION", "BLOCKED"],
    },
    requirement_summary: {
      type: "string",
    },
    scope: {
      type: "object",
      additionalProperties: false,
      required: ["modules", "systems", "environments", "project"],
      properties: {
        modules: {
          type: "array",
          items: { type: "string" },
        },
        systems: {
          type: "array",
          items: { type: "string" },
        },
        environments: {
          type: "array",
          items: { type: "string" },
        },
        project: {
          type: ["string", "null"],
        },
      },
    },
    claims: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        required: [
          "id",
          "classification",
          "statement",
          "system_specific",
          "evidence_refs",
          "source_refs",
        ],
        properties: {
          id: { type: "string" },
          classification: {
            enum: ["VERIFIED", "KNOWN", "INFERRED", "ASSUMED"],
          },
          statement: { type: "string" },
          system_specific: { type: "boolean" },
          evidence_refs: {
            type: "array",
            items: { type: "string" },
          },
          source_refs: {
            type: "array",
            items: { type: "string" },
          },
        },
      },
    },
    unknowns: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        required: [
          "id",
          "statement",
          "material",
          "blocks_decision",
          "verification",
        ],
        properties: {
          id: { type: "string" },
          statement: { type: "string" },
          material: { type: "boolean" },
          blocks_decision: { type: "boolean" },
          verification: { type: "string" },
        },
      },
    },
    conflicts: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        required: [
          "id",
          "statement",
          "material",
          "blocks_decision",
          "status",
          "source_refs",
          "verification",
        ],
        properties: {
          id: { type: "string" },
          statement: { type: "string" },
          material: { type: "boolean" },
          blocks_decision: { type: "boolean" },
          status: {
            enum: ["UNRESOLVED", "RESOLVED"],
          },
          source_refs: {
            type: "array",
            items: { type: "string" },
          },
          verification: { type: "string" },
        },
      },
    },
    existing_solution_discovery: {
      type: "object",
      additionalProperties: false,
      required: ["performed", "checks"],
      properties: {
        performed: { type: "boolean" },
        checks: {
          type: "array",
          items: {
            type: "object",
            additionalProperties: false,
            required: ["category", "status", "notes", "evidence_refs"],
            properties: {
              category: {
                enum: [
                  "SAP_STANDARD",
                  "CONFIGURATION",
                  "EXISTING_IMPLEMENTATION",
                  "SUPPORTED_EXTENSION",
                  "RELEASED_API_EVENT",
                  "SIDE_BY_SIDE_EXTENSION",
                  "CUSTOM_IMPLEMENTATION",
                ],
              },
              status: {
                enum: ["APPLICABLE", "NOT_APPLICABLE", "UNKNOWN"],
              },
              notes: { type: "string" },
              evidence_refs: {
                type: "array",
                items: { type: "string" },
              },
            },
          },
        },
      },
    },
    solution_options: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        required: [
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
        properties: {
          id: { type: "string" },
          title: { type: "string" },
          family: {
            enum: [
              "STANDARD_CONFIGURATION",
              "SUPPORTED_EXTENSION",
              "RELEASED_API_EVENT",
              "INTEGRATION",
              "SIDE_BY_SIDE_BTP",
              "CUSTOM_IMPLEMENTATION",
              "OTHER",
            ],
          },
          description: { type: "string" },
          tradeoffs: {
            type: "array",
            items: { type: "string" },
          },
          risks: {
            type: "array",
            items: { type: "string" },
          },
          evidence_refs: {
            type: "array",
            items: { type: "string" },
          },
          assumption_refs: {
            type: "array",
            items: { type: "string" },
          },
          required_verification: {
            type: "array",
            items: { type: "string" },
          },
        },
      },
    },
    proposal: {
      anyOf: [
        { type: "null" },
        {
          type: "object",
          additionalProperties: false,
          required: [
            "selected_option_id",
            "summary",
            "rationale",
            "confidence",
            "evidence_refs",
            "assumption_refs",
          ],
          properties: {
            selected_option_id: { type: "string" },
            summary: { type: "string" },
            rationale: {
              type: "array",
              items: { type: "string" },
            },
            confidence: {
              enum: ["LOW", "MEDIUM", "HIGH"],
            },
            evidence_refs: {
              type: "array",
              items: { type: "string" },
            },
            assumption_refs: {
              type: "array",
              items: { type: "string" },
            },
          },
        },
      ],
    },
    required_verification: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        required: ["id", "description", "why", "blocking"],
        properties: {
          id: { type: "string" },
          description: { type: "string" },
          why: { type: "string" },
          blocking: { type: "boolean" },
        },
      },
    },
    implementation_handoff: {
      type: "object",
      additionalProperties: false,
      required: ["ready", "notes"],
      properties: {
        ready: { type: "boolean" },
        notes: {
          type: "array",
          items: { type: "string" },
        },
      },
    },
    requested_capabilities: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        required: ["verb", "purpose"],
        properties: {
          verb: {
            enum: ["READ", "QUERY", "ANALYZE", "PROPOSE"],
          },
          purpose: { type: "string" },
        },
      },
    },
    next_action: {
      type: "object",
      additionalProperties: false,
      required: ["type", "description"],
      properties: {
        type: {
          enum: [
            "REQUEST_CLARIFICATION",
            "VERIFY_CONTEXT",
            "REVIEW_ARCHITECTURE",
            "HANDOFF_IMPLEMENTATION",
            "NONE",
          ],
        },
        description: { type: "string" },
      },
    },
  },
} as const;

const INSTRUCTIONS = [
  "Act as the SAP Technical Architect reasoning component for one bounded invocation.",
  "Return only the semantic draft described by the supplied JSON Schema.",
  "Do not create contract_version, task_id, or provenance; the runtime owns those fields.",
  "Use only evidence IDs and source references present in the supplied input.",
  "Do not invent system-specific SAP object identifiers as verified facts.",
  "If material uncertainty prevents a defensible proposal, return BLOCKED or NEEDS_CLARIFICATION with proposal=null.",
  "Requested capabilities may only use READ, QUERY, ANALYZE, or PROPOSE.",
].join(" ");

export class OpenAIProviderConfigurationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "OpenAIProviderConfigurationError";
  }
}

export class OpenAIProviderResponseError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "OpenAIProviderResponseError";
  }
}

export interface OpenAIProviderOptions {
  apiKey: string;
  model: string;
  fetchImpl?: typeof fetch;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function extractOutputText(value: unknown): string {
  if (!isRecord(value)) {
    throw new OpenAIProviderResponseError(
      "OpenAI response payload must be an object.",
    );
  }

  if (value.status !== undefined && value.status !== "completed") {
    throw new OpenAIProviderResponseError(
      `OpenAI response did not complete successfully: ${String(value.status)}.`,
    );
  }

  if (!Array.isArray(value.output)) {
    throw new OpenAIProviderResponseError(
      "OpenAI response did not contain an output array.",
    );
  }

  const outputTexts: string[] = [];
  let refusalSeen = false;

  for (const item of value.output) {
    if (!isRecord(item) || item.type !== "message" || !Array.isArray(item.content)) {
      continue;
    }

    for (const content of item.content) {
      if (!isRecord(content)) {
        continue;
      }

      if (content.type === "refusal") {
        refusalSeen = true;
        continue;
      }

      if (
        content.type === "output_text" &&
        typeof content.text === "string"
      ) {
        outputTexts.push(content.text);
      }
    }
  }

  if (refusalSeen) {
    throw new OpenAIProviderResponseError(
      "OpenAI provider refused the structured response.",
    );
  }

  if (outputTexts.length !== 1) {
    throw new OpenAIProviderResponseError(
      `OpenAI response must contain exactly one output_text block; received ${outputTexts.length}.`,
    );
  }

  return outputTexts[0]!;
}

export class OpenAIProvider implements ProviderAdapter {
  readonly id = OPENAI_PROVIDER_ID;
  readonly version = OPENAI_PROVIDER_VERSION;

  private readonly fetchImpl: typeof fetch;

  constructor(private readonly options: OpenAIProviderOptions) {
    this.fetchImpl = options.fetchImpl ?? globalThis.fetch;
  }

  async invoke(
    input: Readonly<TechnicalArchitectInput>,
  ): Promise<unknown> {
    const apiKey = this.options.apiKey.trim();
    const model = this.options.model.trim();

    if (apiKey.length === 0) {
      throw new OpenAIProviderConfigurationError(
        "OPENAI_API_KEY is not configured.",
      );
    }

    if (model.length === 0) {
      throw new OpenAIProviderConfigurationError(
        "OpenAI model is not configured.",
      );
    }

    const response = await this.fetchImpl(OPENAI_RESPONSES_ENDPOINT, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model,
        instructions: INSTRUCTIONS,
        input: JSON.stringify(input),
        reasoning: {
          effort: "medium",
        },
        store: false,
        stream: false,
        text: {
          format: {
            type: "json_schema",
            name: "technical_architect_draft",
            strict: true,
            schema: DRAFT_SCHEMA,
          },
        },
      }),
    });

    if (!response.ok) {
      throw new OpenAIProviderResponseError(
        `OpenAI Responses API returned HTTP ${response.status}.`,
      );
    }

    let payload: unknown;

    try {
      payload = await response.json();
    } catch {
      throw new OpenAIProviderResponseError(
        "OpenAI response body was not valid JSON.",
      );
    }

    return extractOutputText(payload);
  }
}

export const OPENAI_TECHNICAL_ARCHITECT_DRAFT_SCHEMA = DRAFT_SCHEMA;
