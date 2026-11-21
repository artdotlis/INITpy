// SPDX-FileCopyrightText: 2026 Artur Lissin
//
// SPDX-License-Identifier: Unlicense

import { execFileSync } from 'node:child_process'
import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { beforeAll, describe, expect, it } from 'vitest'

const repo = fileURLToPath(new URL('../../../../', import.meta.url))
const read = (path: string) => readFileSync(join(repo, path), 'utf-8')

describe('docs build', () => {
    beforeAll(() => {
        execFileSync('just', ['run-docs'], {
            cwd: repo,
            env: { ...process.env, CONTAINER: 'container' },
            stdio: 'pipe',
        })
    }, 120_000)

    it('publishes the README without badge lines as a partial', () => {
        const readme = read('README.md')
            .split('\n')
            .filter((line) => !line.startsWith('[!['))
            .join('\n')
        expect(read('packages/docs/src/_partials/readme.md')).toBe(readme)
    })

    it('publishes the LICENSE as a partial', () => {
        expect(read('packages/docs/src/_partials/license.md')).toBe(read('LICENSE'))
    })

    it('renders the partials into the built pages', () => {
        const heading = (md: string) =>
            md.split('\n').find((line) => line.trim())!.replace(/^#+\s*/, '')
        expect(read('public/docs/about.html')).toContain(heading(read('README.md')))
        expect(read('public/docs/license.html')).toContain(heading(read('LICENSE')))
    })
})
