import type { TechnicalArchitectInput } from "./contracts.js";
import type { ProviderAdapter } from "./provider-adapter.js";

export type FixtureProviderBehavior =
  | {
      kind: "output";
      value: unknown;
    }
  | {
      kind: "error";
      error: Error;
    };

export class FixtureProvider implements ProviderAdapter {
  readonly id = "fixture";
  readonly version = "1";
  attempts = 0;

  constructor(private readonly behavior: FixtureProviderBehavior) {}

  async invoke(
    _input: Readonly<TechnicalArchitectInput>,
  ): Promise<unknown> {
    this.attempts += 1;

    if (this.behavior.kind === "error") {
      throw this.behavior.error;
    }

    return structuredClone(this.behavior.value);
  }
}
