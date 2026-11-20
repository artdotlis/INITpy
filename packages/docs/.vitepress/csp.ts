// SPDX-FileCopyrightText: 2026 Artur Lissin
//
// SPDX-License-Identifier: Unlicense

import { randomBytes } from 'node:crypto'

/** Stamp a built page with a self-only CSP (nonce on inline scripts). Idempotent. */
export function injectCsp(html: string): string {
    if (html.includes('<meta http-equiv="Content-Security-Policy"')) return html
    const nonce = randomBytes(16).toString('base64')
    const stamped = html.replace(/<script(?![^>]*\ssrc=)([^>]*)>/g, (m: string) =>
        m.replace('>', ` nonce="${nonce}">`)
    )

    const policy =
        `default-src 'none'; ` +
        `script-src 'self' 'nonce-${nonce}'; ` +
        `style-src 'self' 'unsafe-inline'; ` +
        `img-src 'self' data:; ` +
        `font-src 'self' data:; ` +
        `connect-src 'self'; ` +
        `form-action 'none'; ` +
        `base-uri 'none'; ` +
        `frame-ancestors 'none'; ` +
        `object-src 'none'; ` +
        `upgrade-insecure-requests`
    const meta =
        `<meta http-equiv="Content-Security-Policy" content="${policy}">` +
        `\n    <meta name="referrer" content="strict-origin-when-cross-origin">`
    return stamped.replace(/<head([^>]*)>/, `<head$1>\n    ${meta}`)
}
