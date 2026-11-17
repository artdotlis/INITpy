// SPDX-FileCopyrightText: 2026 Artur Lissin
//
// SPDX-License-Identifier: Unlicense

export type IconName =
    | 'info'
    | 'house'
    | 'share'
    | 'search'
    | 'database'
    | 'export'
    | 'dna'
    | 'pill'
    | 'flask'
    | 'archive'
    | 'code'
    | 'quotes'
    | 'phone'

/** Tone names. Map to the CSS var `--dd-ico-<name>` (light + dark) in style.css. */
export type ToneName = 'primary' | 'signal' | 'muted' | 'graphite' | 'danger'

/** An icon + tone selected together in config. */
export type IconPreset = { name: IconName; tone: ToneName }

/** CSS custom-property value for a tone, e.g. `var(--dd-ico-primary)`. */
export const toneVar = (tone: string) => `var(--dd-ico-${tone})`

/** Tone of an icon preset. */
export const iconTone = (preset: IconPreset): ToneName => preset.tone

// Every icon is available in every tone, so colour is a per-usage choice.
const variants = (name: IconName) => ({
    primary: { name, tone: 'primary' as ToneName },
    signal: { name, tone: 'signal' as ToneName },
    muted: { name, tone: 'muted' as ToneName },
    graphite: { name, tone: 'graphite' as ToneName },
    danger: { name, tone: 'danger' as ToneName },
})

export const Icon: Record<IconName, Record<ToneName, IconPreset>> = {
    info: variants('info'),
    house: variants('house'),
    share: variants('share'),
    search: variants('search'),
    database: variants('database'),
    export: variants('export'),
    dna: variants('dna'),
    pill: variants('pill'),
    flask: variants('flask'),
    archive: variants('archive'),
    code: variants('code'),
    quotes: variants('quotes'),
    phone: variants('phone'),
}
