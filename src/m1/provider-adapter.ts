import type { TechnicalArchitectInput } from "./contracts.js";

export interface ProviderAdapter {
  readonly id: string;
  readonly version: string;

  invoke(input: Readonly<TechnicalArchitectInput>): Promise<unknown>;
}
