#!/usr/bin/env node

import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const EXPECTED = Object.freeze({
  node: "24.21.0",
  npm: "11.19.0",
  typescript: "7.0.2",
  tests: 11,
});

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(SCRIPT_DIR, "..");
const REPORT_PATH = resolve(ROOT, "build", "m1-reference-harness-verification.json");
const npmCommand = process.platform === "win32" ? "npm.cmd" : "npm";

function clip(value, max = 50000) {
  const text = value ?? "";
  return text.length <= max ? text : `${text.slice(0, max)}\n...[truncated]`;
}

function run(command, args, options = {}) {
  const startedAt = new Date().toISOString();
  const result = spawnSync(command, args, {
    cwd: ROOT,
    encoding: "utf8",
    maxBuffer: 16 * 1024 * 1024,
    env: process.env,
    ...options,
  });
  const finishedAt = new Date().toISOString();

  const record = {
    command: [command, ...args],
    started_at: startedAt,
    finished_at: finishedAt,
    exit_code: result.status,
    signal: result.signal,
    error: result.error ? String(result.error.message ?? result.error) : null,
    stdout: clip(result.stdout),
    stderr: clip(result.stderr),
  };

  if (record.stdout) process.stdout.write(record.stdout);
  if (record.stderr) process.stderr.write(record.stderr);

  return record;
}

function sha256File(path) {
  return `sha256:${createHash("sha256").update(readFileSync(path)).digest("hex")}`;
}

function commandSucceeded(record) {
  return record.exit_code === 0 && record.error === null;
}

function outputText(record) {
  return `${record.stdout ?? ""}${record.stderr ?? ""}`.trim();
}

const report = {
  schema_version: "m1.reference-harness-verification.v1",
  started_at: new Date().toISOString(),
  finished_at: null,
  overall: "FAIL",
  expected_toolchain: EXPECTED,
  observed_toolchain: {
    node: process.versions.node,
    npm: null,
    typescript: null,
  },
  test_summary: {
    tests: null,
    pass: null,
    fail: null,
  },
  revision: {
    git_sha: null,
    clean_before: false,
    clean_after: false,
  },
  artifact_fingerprints: {
    package_json: null,
    package_lock_json: null,
  },
  checks: [],
  failure_reasons: [],
};

function fail(reason) {
  report.failure_reasons.push(reason);
}

function addCheck(name, record) {
  report.checks.push({ name, ...record });
  return record;
}

try {
  report.artifact_fingerprints.package_json = sha256File(resolve(ROOT, "package.json"));
  report.artifact_fingerprints.package_lock_json = sha256File(resolve(ROOT, "package-lock.json"));

  const gitSha = addCheck("git_revision", run("git", ["rev-parse", "HEAD"]));
  if (commandSucceeded(gitSha)) {
    report.revision.git_sha = outputText(gitSha).split(/\r?\n/)[0] ?? null;
  } else {
    fail("Unable to resolve git revision.");
  }

  const cleanBefore = addCheck("git_clean_before", run("git", ["status", "--porcelain"]));
  if (commandSucceeded(cleanBefore) && outputText(cleanBefore) === "") {
    report.revision.clean_before = true;
  } else {
    fail("Working tree is not clean before verification.");
  }

  if (report.observed_toolchain.node !== EXPECTED.node) {
    fail(`Node version mismatch: expected ${EXPECTED.node}, observed ${report.observed_toolchain.node}.`);
  }

  const npmVersion = addCheck("npm_version", run(npmCommand, ["--version"]));
  if (commandSucceeded(npmVersion)) {
    report.observed_toolchain.npm = outputText(npmVersion).split(/\r?\n/)[0] ?? null;
    if (report.observed_toolchain.npm !== EXPECTED.npm) {
      fail(`npm version mismatch: expected ${EXPECTED.npm}, observed ${report.observed_toolchain.npm}.`);
    }
  } else {
    fail("Unable to execute npm.");
  }

  const preconditionsOk =
    report.revision.git_sha !== null &&
    report.revision.clean_before &&
    report.observed_toolchain.node === EXPECTED.node &&
    report.observed_toolchain.npm === EXPECTED.npm;

  if (preconditionsOk) {
    const npmCi = addCheck("npm_ci", run(npmCommand, ["ci", "--ignore-scripts"]));
    if (!commandSucceeded(npmCi)) {
      fail("npm ci failed.");
    }

    if (commandSucceeded(npmCi)) {
      const tscVersion = addCheck(
        "typescript_version",
        run(process.execPath, [resolve(ROOT, "node_modules", "typescript", "bin", "tsc"), "--version"]),
      );

      if (commandSucceeded(tscVersion)) {
        const match = outputText(tscVersion).match(/Version\s+([^\s]+)/);
        report.observed_toolchain.typescript = match?.[1] ?? null;
        if (report.observed_toolchain.typescript !== EXPECTED.typescript) {
          fail(
            `TypeScript version mismatch: expected ${EXPECTED.typescript}, observed ${report.observed_toolchain.typescript}.`,
          );
        }
      } else {
        fail("Unable to execute the installed TypeScript compiler.");
      }

      if (report.observed_toolchain.typescript === EXPECTED.typescript) {
        const check = addCheck("npm_run_check", run(npmCommand, ["run", "check"]));
        if (!commandSucceeded(check)) {
          fail("npm run check failed.");
        } else {
          const checkOutput = outputText(check);
          const testsMatch = checkOutput.match(/^\s*(?:#|ℹ)\s+tests\s+(\d+)\s*$/m);
          const passMatch = checkOutput.match(/^\s*(?:#|ℹ)\s+pass\s+(\d+)\s*$/m);
          const failMatch = checkOutput.match(/^\s*(?:#|ℹ)\s+fail\s+(\d+)\s*$/m);
          report.test_summary.tests = testsMatch ? Number(testsMatch[1]) : null;
          report.test_summary.pass = passMatch ? Number(passMatch[1]) : null;
          report.test_summary.fail = failMatch ? Number(failMatch[1]) : null;

          if (report.test_summary.tests !== EXPECTED.tests) {
            fail(`Test-count mismatch: expected ${EXPECTED.tests}, observed ${report.test_summary.tests}.`);
          }
          if (report.test_summary.pass !== EXPECTED.tests || report.test_summary.fail !== 0) {
            fail(
              `Test summary mismatch: expected ${EXPECTED.tests} pass / 0 fail, observed ${report.test_summary.pass} pass / ${report.test_summary.fail} fail.`,
            );
          }
        }
      }
    }
  }

  const cleanAfter = addCheck("git_clean_after", run("git", ["status", "--porcelain"]));
  if (commandSucceeded(cleanAfter) && outputText(cleanAfter) === "") {
    report.revision.clean_after = true;
  } else {
    fail("Working tree changed during verification.");
  }

  if (
    report.failure_reasons.length === 0 &&
    report.revision.clean_before &&
    report.revision.clean_after &&
    report.observed_toolchain.node === EXPECTED.node &&
    report.observed_toolchain.npm === EXPECTED.npm &&
    report.observed_toolchain.typescript === EXPECTED.typescript
  ) {
    report.overall = "PASS";
  }
} catch (error) {
  fail(error instanceof Error ? error.message : String(error));
} finally {
  report.finished_at = new Date().toISOString();
  mkdirSync(resolve(ROOT, "build"), { recursive: true });
  writeFileSync(REPORT_PATH, `${JSON.stringify(report, null, 2)}\n`, "utf8");
  console.log(`\nVerification report: ${REPORT_PATH}`);
  console.log(`Overall: ${report.overall}`);
  if (report.failure_reasons.length > 0) {
    for (const reason of report.failure_reasons) console.error(`- ${reason}`);
  }
}

process.exitCode = report.overall === "PASS" ? 0 : 1;
