// SPDX-FileCopyrightText: 2026 Artur Lissin
//
// SPDX-License-Identifier: Unlicense

import { readFileSync } from 'node:fs'
import { describe, expect, it } from 'vitest'

const root = new URL('../../../', import.meta.url)
const docs = new URL('../', import.meta.url)
const read = (base: URL, path: string) => readFileSync(new URL(path, base), 'utf-8')

describe('docs partials', () => {
  it('license partial is the root LICENSE', () => {
    expect(read(docs, 'src/_partials/license.md')).toBe(read(root, 'LICENSE'))
  })

  it('license page includes the partial', () => {
    const page = read(docs, 'src/license.md')
    expect(page).toContain('# License')
    expect(page).toContain('<!-- @include: _partials/license.md -->')
  })

  it('readme partial is the README without badge lines', () => {
    const readme = read(root, 'README.md')
      .split('\n')
      .filter((line) => !line.startsWith('[!['))
      .join('\n')
    expect(read(docs, 'src/_partials/readme.md')).toBe(readme)
  })
})
