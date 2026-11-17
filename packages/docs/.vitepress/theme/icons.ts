// SPDX-FileCopyrightText: 2026 Artur Lissin
//
// SPDX-License-Identifier: Unlicense

// Icon + tone library for the docs theme. Select an icon in config with a
// single constant; its tone (color) travels with it. SSR-safe: only string
// constants and maps here — the Phosphor components are resolved client-side
// in SidebarIcon.vue, so this file stays out of the Vite Node graph.

/** Tone names. Map to the CSS var `--dd-ico-<name>` (light + dark) in style.css. */
export const Tone = {
    primary: 'primary',
    signal: 'signal',
    muted: 'muted',
    graphite: 'graphite',
    danger: 'danger',
} as const
export type ToneName = (typeof Tone)[keyof typeof Tone]

/** CSS custom-property value for a tone, e.g. `var(--dd-ico-primary)`. */
export const toneVar = (tone: string) => `var(--dd-ico-${tone})`

/** Icon names. Selectable in config; each resolves to a Phosphor icon. */
export const Icon = {
    code: 'code',
    file: 'file',
    info: 'info',
    book: 'book',
    terminal: 'terminal',
    gear: 'gear',
    cpu: 'cpu',
    database: 'database',
    gitBranch: 'gitBranch',
    function: 'function',
    cube: 'cube',
    wrench: 'wrench',
    shield: 'shield',
    key: 'key',
    pulse: 'pulse',
    chart: 'chart',
    rocket: 'rocket',
    globe: 'globe',
    star: 'star',
    users: 'users',
    trophy: 'trophy',
    archive: 'archive',
} as const
export type IconName = (typeof Icon)[keyof typeof Icon]

/** Each icon's tone (role color) — so config picks one constant and the
 * color follows. Edit here to recolor an icon across the whole site. */
export const ICON_TONES: Record<IconName, ToneName> = {
    code: Tone.danger,
    file: Tone.signal,
    info: Tone.muted,
    book: Tone.primary,
    terminal: Tone.graphite,
    gear: Tone.graphite,
    cpu: Tone.primary,
    database: Tone.primary,
    gitBranch: Tone.signal,
    function: Tone.graphite,
    cube: Tone.primary,
    wrench: Tone.signal,
    shield: Tone.primary,
    key: Tone.danger,
    pulse: Tone.danger,
    chart: Tone.primary,
    rocket: Tone.signal,
    globe: Tone.primary,
    star: Tone.signal,
    users: Tone.primary,
    trophy: Tone.signal,
    archive: Tone.muted,
}

/** Tone for an icon name, defaulting to `graphite` for unknown names. */
export const iconTone = (name: string): ToneName =>
    ICON_TONES[name as IconName] ?? Tone.graphite
