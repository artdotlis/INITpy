// SPDX-FileCopyrightText: 2026 Artur Lissin
//
// SPDX-License-Identifier: Unlicense

import type { Theme } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import '@theme/style.css'

const baseOf = () => import.meta.env.BASE_URL

const norm = (h) => {
    if (typeof h !== 'string') return null
    const base = baseOf()
    let p = h
    if (/^https?:\/\//.test(p)) p = new URL(p).pathname
    if (base !== '/' && p.startsWith(base)) p = p.slice(base.length - 1)
    return p
}

const rowOf = (link) => {
    const base = baseOf()
    const hrefOf = (l) => (l.startsWith('/') ? base + l.slice(1) : l)
    const sidebar = link.themeConfig.sidebar
    const rows =
        sidebar && typeof sidebar === 'object' && !Array.isArray(sidebar)
            ? Object.values(sidebar).flat()
            : sidebar || []
    const map = new Map()
    const walk = (items) => {
        for (const item of items || []) {
            if (item.link) map.set(norm(hrefOf(item.link)), item)
            if (item.items) walk(item.items)
        }
    }
    for (const entry of rows) if (entry?.items) walk(entry.items)
    return map
}

const stamp = (map) => {
    for (const row of document.querySelectorAll('.VPSidebarItem a')) {
        const item = map.get(norm(row.getAttribute('href')))
        if (!item) continue
        const el = row.closest('.VPSidebarItem')?.querySelector(':scope > .item')
        if (!el) continue
        const wrap = el.closest('.VPSidebarItem')
        const hasIcon = !!item.icon
        if (wrap.classList.contains('has-icon') !== hasIcon) {
            wrap.classList.toggle('has-icon', hasIcon)
        }
        if (!hasIcon) continue
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

const snap = new WeakSet()

// `--dd-tt` is a style write, not a class/childList mutation, so it cannot re-fire
// the observer below. Zero it for one activation: the tile snaps to its tone
// instead of fading from the neutral base.
const zero = (item) => {
    item.style.setProperty('--dd-tt', '0s')
    requestAnimationFrame(() =>
        requestAnimationFrame(() => item.style.removeProperty('--dd-tt'))
    )
}

export default {
    extends: DefaultTheme,
    enhanceApp({ siteData }) {
        if (import.meta.env.SSR) return
        const map = rowOf(siteData.value)
        new MutationObserver(() => {
            stamp(map)
            for (const t of document.querySelectorAll('.VPSidebarItem')) {
                const item = t.querySelector(':scope > .item')
                if (!item) continue
                if (t.classList.contains('is-active')) {
                    if (snap.has(t)) continue
                    snap.add(t)
                    zero(item)
                } else {
                    snap.delete(t)
                }
            }
        }).observe(document.body, {
            subtree: true,
            childList: true,
            attributes: true,
            attributeFilter: ['class'],
        })
    },
} satisfies Theme
