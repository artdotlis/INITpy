// SPDX-FileCopyrightText: 2026 Artur Lissin
//
// SPDX-License-Identifier: Unlicense

import type { Theme } from 'vitepress'
import { createApp, h } from 'vue'
import DefaultTheme from 'vitepress/theme'
import SidebarIcon from './SidebarIcon.vue'
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

function iconEl(name) {
    const holder = document.createElement('span')
    createApp({ render: () => h(SidebarIcon, { name }) }).mount(holder)
    return holder.firstElementChild
}

function stamp(map) {
    for (const row of document.querySelectorAll('.VPSidebarItem')) {
        const itemEl = row.querySelector(':scope > .item')
        if (!itemEl) continue
        const link = itemEl.querySelector(':scope > .link')
        if (!link) continue
        const entry = map.get(norm(link.getAttribute('href')))
        const hasIcon = !!entry?.icon
        if (row.classList.contains('has-icon') !== hasIcon) {
            row.classList.toggle('has-icon', hasIcon)
        }
        if (!hasIcon) continue
        itemEl.style.setProperty('--dd-ico', `var(--dd-ico-${entry.tone ?? 'graphite'})`)
        if (!itemEl.querySelector('.sidebar-icon')) {
            itemEl.prepend(iconEl(entry.icon))
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
