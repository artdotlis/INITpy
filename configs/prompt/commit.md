<!--
SPDX-FileCopyrightText: 2026 Artur Lissin

SPDX-License-Identifier: CC0-1.0
-->

# Commit Message Generator Prompt

Generate a commit message in the **Conventional Commits 1.0.0** format based on the provided git diff.

---

## Requirements

### Analysis
- Analyze the diff and summarize changes accurately:
  1. Include added, removed, or modified functionality.
  2. Ignore cosmetic changes (whitespace, formatting) unless relevant.
  3. Exclude changes in files matching `requirements*.txt`.

---

### Security Check (MANDATORY)
- Scan the diff for potential secrets, including but not limited to:
  - Passwords
  - API keys
  - Tokens
  - Private keys
  - Hardcoded credentials
- If ANY secret or sensitive value is detected:
  - DO NOT generate a Conventional Commits–compliant message
  - Instead, output a failure message starting with ERROR -
  - The failure message must clearly indicate that a secret was detected
  - This is REQUIRED to prevent unsafe commits
  - Add the source file of the leak

---

### Structure

Your commit message must follow this structure:

1. **Type**  
   One of:
   - feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert

2. **Scope (optional)**  
   - Derived from changed file paths  
   - Example: `feat(auth):`

3. **Title (required)**  
   - One line
   - Lowercase
   - Present tense
   - Concise summary

4. **Body (optional)**  
   - Provide more detailed explanation
   - Explain:
     - WHY the change was made
     - HOW it affects behavior
   - Use uppercase sparingly for emphasis
   - Wrap lines at **100 characters**

5. **Footer (optional)**  
   Include if present in diff:
   - Issue references (e.g., `Closes #123`)
   - Co-authors (`Co-authored-by: Name`)
   - Other relevant metadata

---

### Formatting Rules

- First line must be entirely lowercase
- Follow Conventional Commits strictly
- Do NOT include:
  - Markdown formatting
  - Quotes
  - Extra commentary
- Output **plain text only**
- Do NOT invent breaking changes

---

### Prioritization

1. Functional / behavioral changes over formatting changes
2. Core logic changes over trivial modifications

---

## Example

feat(auth): add user login api

Added support for user login via OAuth2. This allows users to authenticate
using their Google account.

Closes #42

---

## Example (Secret Detected)

ERROR - potential secret detected in diff. commit message generation aborted.
