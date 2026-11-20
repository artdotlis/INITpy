// SPDX-FileCopyrightText: 2026 Artur Lissin
//
// SPDX-License-Identifier: Unlicense

import type { SiteData, Theme } from 'vitepress'
import { createApp, h } from 'vue'
import DefaultTheme from 'vitepress/theme'
import SidebarIcon from '@theme/SidebarIcon.vue'
import { iconTone, toneVar } from '@theme/icons'
import type { IconPreset } from '@theme/icons'
import '@theme/style.css'

/** A single sidebar entry, plus the icon the theme overlays on it. */
interface SidebarRow {
    link?: string
    icon?: IconPreset
    items?: SidebarRow[]
}

/**
 * Reads the site base path the current build was produced with.
 *
 * @returns The base URL, always ending in a slash.
 */
const baseOf = () => import.meta.env.BASE_URL

/**
 * Normalises a sidebar link to the pathname form used as the lookup key.
 *
 * Absolute URLs are reduced to their pathname, and the site base prefix is
 * stripped so base-relative and absolute links compare equal.
 *
 * @param h Raw `href`, from the sidebar config or from the rendered DOM.
 * @returns The normalised pathname, or `null` if `h` is not a string.
 */
const norm = (h: string | null): string | null => {
    if (typeof h !== 'string') return null
    const base = baseOf()
    let p = h
    if (/^https?:\/\//.test(p)) p = new URL(p).pathname
    if (base !== '/' && p.startsWith(base)) p = p.slice(base.length - 1)
    return p
}

/**
 * Indexes the configured sidebar entries by normalised link.
 *
 * @param link Site data provided to the theme by VitePress.
 * @returns A map from normalised pathname to the configured sidebar row.
 */
const rowOf = (link: SiteData): Map<string, SidebarRow> => {
    const base = baseOf()
    const hrefOf = (l: string) => (l.startsWith('/') ? base + l.slice(1) : l)
    const sidebar = link.themeConfig.sidebar
    const rows: SidebarRow[] =
        sidebar && typeof sidebar === 'object' && !Array.isArray(sidebar)
            ? Object.values(sidebar).flat()
            : sidebar || []
    const map = new Map<string, SidebarRow>()
    const walk = (items: SidebarRow[]) => {
        for (const item of items || []) {
            if (item.link) {
                const key = norm(hrefOf(item.link))
                if (key) map.set(key, item)
            }
            if (item.items) walk(item.items)
        }
    }
    for (const entry of rows) if (entry?.items) walk(entry.items)
    return map
}

/**
 * Renders a preset into a detached DOM node.
 *
 * @param preset Icon preset to draw.
 * @returns The rendered icon element, or `null` if the component rendered nothing.
 */
function iconEl(preset: IconPreset): Element | null {
    const holder = document.createElement('span')
    createApp({ render: () => h(SidebarIcon, { preset }) }).mount(holder)
    return holder.firstElementChild
}

/**
 * Syncs the icons, tone CSS variable, and `has-icon` class onto the rendered
 * sidebar after each VitePress re-render.
 *
 * @param map Sidebar rows indexed by normalised link, as built by `rowOf`.
 */
function stamp(map: Map<string, SidebarRow>) {
    for (const row of document.querySelectorAll('.VPSidebarItem')) {
        const itemEl = row.querySelector<HTMLElement>(':scope > .item')
        if (!itemEl) continue
        const link = itemEl.querySelector<HTMLElement>(':scope > .link')
        if (!link) continue
        const key = norm(link.getAttribute('href'))
        const entry = key ? map.get(key) : undefined
        const icon = entry?.icon
        const hasIcon = !!icon
        if (row.classList.contains('has-icon') !== hasIcon) {
            row.classList.toggle('has-icon', hasIcon)
        }
        if (!icon) continue
        itemEl.style.setProperty('--dd-ico', toneVar(iconTone(icon)))
        if (!itemEl.querySelector('.sidebar-icon')) {
            const el = iconEl(icon)
            if (el) itemEl.prepend(el)
        }
    }
}

/** VitePress theme that extends the default theme with sidebar icons. */
export default {
    extends: DefaultTheme,
    enhanceApp({ siteData }) {
        if (import.meta.env.SSR) return
        const map = rowOf(siteData.value)
        new MutationObserver(() => stamp(map)).observe(document.body, {
            subtree: true,
            childList: true,
            attributes: true,
            attributeFilter: ['class'],
        })
    },
} satisfies Theme
