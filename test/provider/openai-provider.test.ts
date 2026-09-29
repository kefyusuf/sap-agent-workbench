import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import test from "node:test";

import type { TechnicalArchitectInput } from "../../src/m1/contracts.js";
import {
  OPENAI_TECHNICAL_ARCHITECT_DRAFT_SCHEMA,
  OpenAIProvider,
} from "../../src/m1/openai-provider.js";
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

function completedResponse(outputText: string): unknown {
  return {
    status: "completed",
    output: [
      {
        type: "message",
        content: [
          {
            type: "output_text",
            text: outputText,
          },
        ],
      },
    ],
  };
}

function responseFetch(
  payload: unknown,
  status = 200,
): {
  fetchImpl: typeof fetch;
  calls: Array<{ input: string | URL | Request; init: RequestInit | undefined }>;
} {
  const calls: Array<{
    input: string | URL | Request;
    init: RequestInit | undefined;
  }> = [];

  const fetchImpl: typeof fetch = async (input, init) => {
    calls.push({ input, init });

    return new Response(JSON.stringify(payload), {
      status,
      headers: {
        "Content-Type": "application/json",
      },
    });
  };

  return { fetchImpl, calls };
}

test("OpenAI adapter sends one stateless structured Responses request", async () => {
  const input = await readCaseInput("TA-003");
  const fullResult = await readJson(
    "evals/m1/result-examples/valid-blocked.json",
  );
  const draft = semanticDraftFromResult(fullResult);
  const transport = responseFetch(
    completedResponse(JSON.stringify(draft)),
  );

  const provider = new OpenAIProvider({
    apiKey: "test-secret",
    model: "gpt-5.6-terra",
    fetchImpl: transport.fetchImpl,
  });

  const raw = await provider.invoke(input);

  assert.equal(typeof raw, "string");
  assert.deepEqual(JSON.parse(raw as string), draft);
  assert.equal(transport.calls.length, 1);

  const call = transport.calls[0];
  assert.ok(call);
  assert.equal(String(call.input), "https://api.openai.com/v1/responses");
  assert.equal(call.init?.method, "POST");

  const headers = call.init?.headers as Record<string, string>;
  assert.equal(headers.Authorization, "Bearer test-secret");
  assert.equal(headers["Content-Type"], "application/json");

  assert.equal(typeof call.init?.body, "string");
  const body = JSON.parse(call.init?.body as string) as Record<string, unknown>;

  assert.equal(body.model, "gpt-5.6-terra");
  assert.equal(body.store, false);
  assert.equal(body.stream, false);
  assert.deepEqual(body.reasoning, { effort: "medium" });
  assert.deepEqual(JSON.parse(body.input as string), input);

  const text = body.text as {
    format: {
      type: string;
      name: string;
      strict: boolean;
      schema: {
        properties: Record<string, unknown>;
      };
    };
  };

  assert.equal(text.format.type, "json_schema");
  assert.equal(text.format.name, "technical_architect_draft");
  assert.equal(text.format.strict, true);

  assert.equal(
    Object.prototype.hasOwnProperty.call(
      text.format.schema.properties,
      "contract_version",
    ),
    false,
  );
  assert.equal(
    Object.prototype.hasOwnProperty.call(
      text.format.schema.properties,
      "task_id",
    ),
    false,
  );
  assert.equal(
    Object.prototype.hasOwnProperty.call(
      text.format.schema.properties,
      "provenance",
    ),
    false,
  );

  assert.equal(
    Object.prototype.hasOwnProperty.call(
      OPENAI_TECHNICAL_ARCHITECT_DRAFT_SCHEMA.properties,
      "status",
    ),
    true,
  );
});

test("OpenAI structured draft passes the existing M1 runtime path", async () => {
  const input = await readCaseInput("TA-003");
  const fullResult = await readJson(
    "evals/m1/result-examples/valid-blocked.json",
  );
  const draft = semanticDraftFromResult(fullResult);
  const transport = responseFetch(
    completedResponse(JSON.stringify(draft)),
  );

  const provider = new OpenAIProvider({
    apiKey: "test-secret",
    model: "gpt-5.6-terra",
    fetchImpl: transport.fetchImpl,
  });

  const outcome = await executeTechnicalArchitect(input, provider);

  assert.equal(outcome.ok, true);
  assert.equal(transport.calls.length, 1);

  if (!outcome.ok) {
    return;
  }

  assert.equal(outcome.result.status, "BLOCKED");
  assert.equal(outcome.result.task_id, "TA-003");
  assert.equal(outcome.execution.adapter_id, "openai-responses");
  assert.equal(outcome.execution.attempts, 1);
});

test("OpenAI HTTP failure maps to existing PROVIDER_FAILURE", async () => {
  const input = await readCaseInput("TA-003");
  const transport = responseFetch(
    {
      error: {
        message: "rate limited",
      },
    },
    429,
  );

  const provider = new OpenAIProvider({
    apiKey: "test-secret",
    model: "gpt-5.6-terra",
    fetchImpl: transport.fetchImpl,
  });

  const outcome = await executeTechnicalArchitect(input, provider);

  assert.equal(outcome.ok, false);
  assert.equal(transport.calls.length, 1);

  if (outcome.ok) {
    return;
  }

  assert.equal(outcome.code, "PROVIDER_FAILURE");
  assert.equal(outcome.stage, "PROVIDER_INVOCATION");
  assert.match(outcome.message, /HTTP 429/);
});

test("missing OpenAI credential fails before network invocation", async () => {
  const input = await readCaseInput("TA-003");
  const transport = responseFetch(completedResponse("{}"));

  const provider = new OpenAIProvider({
    apiKey: "   ",
    model: "gpt-5.6-terra",
    fetchImpl: transport.fetchImpl,
  });

  const outcome = await executeTechnicalArchitect(input, provider);

  assert.equal(outcome.ok, false);
  assert.equal(transport.calls.length, 0);

  if (outcome.ok) {
    return;
  }

  assert.equal(outcome.code, "PROVIDER_FAILURE");
  assert.match(outcome.message, /OPENAI_API_KEY/);
});

test("OpenAI refusal is exposed as provider failure without repair", async () => {
  const input = await readCaseInput("TA-003");
  const transport = responseFetch({
    status: "completed",
    output: [
      {
        type: "message",
        content: [
          {
            type: "refusal",
            refusal: "cannot comply",
          },
        ],
      },
    ],
  });

  const provider = new OpenAIProvider({
    apiKey: "test-secret",
    model: "gpt-5.6-terra",
    fetchImpl: transport.fetchImpl,
  });

  const outcome = await executeTechnicalArchitect(input, provider);

  assert.equal(outcome.ok, false);
  assert.equal(transport.calls.length, 1);

  if (outcome.ok) {
    return;
  }

  assert.equal(outcome.code, "PROVIDER_FAILURE");
  assert.match(outcome.message, /refused/);
});

test("invalid OpenAI response shape fails explicitly", async () => {
  const input = await readCaseInput("TA-003");
  const transport = responseFetch({
    status: "completed",
    output: [],
  });

  const provider = new OpenAIProvider({
    apiKey: "test-secret",
    model: "gpt-5.6-terra",
    fetchImpl: transport.fetchImpl,
  });

  const outcome = await executeTechnicalArchitect(input, provider);

  assert.equal(outcome.ok, false);
  assert.equal(transport.calls.length, 1);

  if (outcome.ok) {
    return;
  }

  assert.equal(outcome.code, "PROVIDER_FAILURE");
  assert.match(outcome.message, /exactly one output_text/);
});
