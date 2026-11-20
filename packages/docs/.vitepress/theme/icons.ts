// SPDX-FileCopyrightText: 2026 Artur Lissin
//
// SPDX-License-Identifier: Unlicense

/**
 * Names of the icons the theme can render in the sidebar.
 *
 * Each name is resolved to a Phosphor component by `SidebarIcon.vue`.
 */
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

/**
 * Colour tones an icon can be drawn in.
 *
 * Each tone maps to the CSS custom property `--dd-ico-<tone>`, defined for the
 * light and dark themes in `style.css`.
 */
export type ToneName = 'primary' | 'signal' | 'muted' | 'graphite' | 'danger'

/** An icon name paired with the tone it is drawn in. */
export type IconPreset = { name: IconName; tone: ToneName }

/**
 * Builds the CSS `var()` reference that resolves to a tone's colour.
 *
 * @param tone Tone name, used verbatim as the `--dd-ico-<tone>` suffix.
 * @returns A CSS `var()` expression for the tone colour.
 */
export const toneVar = (tone: string) => `var(--dd-ico-${tone})`

/**
 * Reads the tone a preset is drawn in.
 *
 * @param preset Icon preset to inspect.
 * @returns The preset's tone name.
 */
export const iconTone = (preset: IconPreset): ToneName => preset.tone

/**
 * Expands one icon name into its per-tone presets.
 *
 * Every icon is available in every tone, so colour stays a per-usage choice.
 */
const variants = (name: IconName) => ({
    primary: { name, tone: 'primary' as ToneName },
    signal: { name, tone: 'signal' as ToneName },
    muted: { name, tone: 'muted' as ToneName },
    graphite: { name, tone: 'graphite' as ToneName },
    danger: { name, tone: 'danger' as ToneName },
})

/**
 * Icon presets, addressed as `Icon.<name>.<tone>`.
 *
 * @example
 * Icon.info.muted
 */
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
