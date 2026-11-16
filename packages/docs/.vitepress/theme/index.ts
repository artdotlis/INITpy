// SPDX-FileCopyrightText: 2026 Artur Lissin
//
// SPDX-License-Identifier: Unlicense

import type { Theme } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import '@theme/style.css'

/*
 * VitePress has no per-sidebar-item icon, so presentation is stamped on the
 * client: each sidebar item may carry `icon`, `tone` and `activeTone` in the
 * config, and we join them onto the rendered row by its own link. The CSS in
 * style.css only reads the resulting `--dd-icon` / `--dd-ico` variables, which
 * keeps the theme page-agnostic — a scaffolded site declares its own items and
 * gets icons for free.
 *
 * Timing matters. The per-item tone/activeTone only becomes visible when a row
 * is active, so the stamp must land before the browser paints the frame in
 * which `is-active` is set. Vue commits that class change from a microtask, and
 * a `MutationObserver` callback is also a microtask, so it fires before paint —
 * the tile shows its own colour in the same frame the highlight appears.
 * Deferring to `requestAnimationFrame` (or `nextTick`) instead fires after
 * paint, leaving a frame where the active tile shows the CSS default colour:
 * the visible flash.
 */
const rowOf = (link) => {
    const base = import.meta.env.BASE_URL
    const hrefOf = (l) => (l.startsWith('/') ? base + l.slice(1) : l)

    const sidebar = link.themeConfig.sidebar
    const rows =
        sidebar && typeof sidebar === 'object' && !Array.isArray(sidebar)
            ? Object.values(sidebar).flat()
            : sidebar || []
    const map = new Map()
    const walk = (items) => {
        for (const item of items || []) {
            if (item.link) map.set(hrefOf(item.link), item)
            if (item.items) walk(item.items)
        }
    }
    for (const entry of rows) if (entry?.items) walk(entry.items)

    return map
}

const stamp = (map) => {
    for (const row of document.querySelectorAll('.VPSidebarItem a')) {
        const item = map.get(row.getAttribute('href'))
        if (!item) continue
        const el = row.closest('.VPSidebarItem')?.querySelector(':scope > .item')
        if (!el) continue
        el.style.setProperty('--dd-icon', `var(--dd-icon-${item.icon})`)
        el.style.setProperty('--dd-ico', `var(--dd-ico-${item.tone})`)
        if (item.activeTone) {
            el.style.setProperty(
                '--dd-ico-active',
                `var(--dd-ico-${item.activeTone})`
            )
        }
    }
}

export default {
    extends: DefaultTheme,
    enhanceApp({ app, siteData }) {
        // Browser-only: no DOM during SSR / static generation.
        if (import.meta.env.SSR) return

        const map = rowOf(siteData.value)

        // Stamp the row as soon as its active state flips (a microtask, before
        // paint), so the highlight never flashes the default colour.
        new MutationObserver(() => stamp(map)).observe(
            document.querySelector('.VPSidebar') ?? document.body,
            { subtree: true, attributes: true, attributeFilter: ['class'] }
        )

        // First paint: stamp every row once the default theme has committed.
        app.mixin({
            mounted() {
                if (this.$el?.id === 'app') requestAnimationFrame(() => stamp(map))
            },
        })
    },
} satisfies Theme
