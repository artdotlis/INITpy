// SPDX-FileCopyrightText: 2026 Artur Lissin
//
// SPDX-License-Identifier: Unlicense

import type { SiteData, Theme } from 'vitepress'
import { createApp, h } from 'vue'
import DefaultTheme from 'vitepress/theme'
import SidebarIcon from './SidebarIcon.vue'
import { iconTone, toneVar } from './icons'
import type { IconPreset } from './icons'
import '@theme/style.css'

interface SidebarRow {
    link?: string
    icon?: IconPreset
    items?: SidebarRow[]
}

const baseOf = () => import.meta.env.BASE_URL

const norm = (h: string | null): string | null => {
    if (typeof h !== 'string') return null
    const base = baseOf()
    let p = h
    if (/^https?:\/\//.test(p)) p = new URL(p).pathname
    if (base !== '/' && p.startsWith(base)) p = p.slice(base.length - 1)
    return p
}

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

function iconEl(preset: IconPreset): Element | null {
    const holder = document.createElement('span')
    createApp({ render: () => h(SidebarIcon, { preset }) }).mount(holder)
    return holder.firstElementChild
}

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
