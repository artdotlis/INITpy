// SPDX-FileCopyrightText: 2026 Artur Lissin
//
// SPDX-License-Identifier: Unlicense

/// <reference types="vite/client" />

declare module '*.css' {
    const css: Record<string, string>
    export default css
}
