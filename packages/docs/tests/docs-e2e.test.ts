// SPDX-FileCopyrightText: 2026 Artur Lissin
//
// SPDX-License-Identifier: Unlicense

import { execFileSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { beforeAll, describe, expect, it } from "vitest";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../../..");
const ARTIFACT_DIR = resolve(ROOT, "public", "docs");

function buildDocs(): void {
  execFileSync("make", ["run-docs"], {
    cwd: ROOT,
    env: { ...process.env, CONTAINER: "container" },
    stdio: "pipe",
  });
}

beforeAll(buildDocs, 600_000);

describe("docs build e2e", () => {
  it("builds the site and ships the README", () => {
    const about = resolve(ARTIFACT_DIR, "about.html");
    expect(existsSync(about)).toBe(true);
    expect(readFileSync(about, "utf8")).toContain(
      "minimal, opinionated project layout",
    );
  });

  it("builds the site and ships the LICENSE", () => {
    const license = resolve(ARTIFACT_DIR, "license.html");
    expect(existsSync(license)).toBe(true);
    expect(readFileSync(license, "utf8")).toContain(
      "free and unencumbered software released into the public domain",
    );
  });
});
