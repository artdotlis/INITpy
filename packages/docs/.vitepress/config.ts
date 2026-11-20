// SPDX-FileCopyrightText: 2026 Artur Lissin
//
// SPDX-License-Identifier: Unlicense

import { DefaultTheme, defineConfig } from 'vitepress'
import { Icon, type IconName, type IconPreset, type ToneName } from './theme/icons'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { resolve, dirname } from 'node:path'
import toml from 'toml'
import { injectCsp } from './csp'

const CONFIG_DIR = dirname(fileURLToPath(import.meta.url))
const ROOT = resolve(CONFIG_DIR, '..')
const THEME_DIR = resolve(CONFIG_DIR, 'theme')
const OUT_DIR = fileURLToPath(new URL('../../../public/docs/', import.meta.url))

// transformHtml is the only VitePress hook that sees the final page HTML.

const transformHtml = (code: string) => injectCsp(code)

const config = toml.parse(
  readFileSync(new URL('./config.toml', import.meta.url), 'utf-8')
) as {
  site?: Record<string, unknown>
  vitepress?: {
    base?: string
    cleanUrls?: boolean
    srcDir?: string
    themeConfig?: {
      logo?: DefaultTheme.ThemeableImage
      search?: { provider: 'local' }
      socialLinks?: Array<{ icon: string; link: string }>
      nav?: Array<{ text: string; link: string }>
      refPackages?: Array<{ name: string; icon?: string; tone?: string }>
      docFooter?: { prev?: boolean; next?: boolean }
      footer?: Array<{ copyright: string }>
    }
  }
}

const site = config.site || {}
const vp = config.vitepress || {}
const tc = vp.themeConfig || {}
const nav = tc.nav as Array<{ text: string; link: string }>
const socialLinks = tc.socialLinks as Array<{ icon: string; link: string }>
const footer = Array.isArray(tc.footer) ? tc.footer[0] || {} : tc.footer || {}
const refPackages = tc.refPackages || []

type SideItem = {
    text: string
    link: string
    icon: IconPreset
}

const preset = (icon: string | undefined, tone: string | undefined): IconPreset | null =>
  icon && icon in Icon ? Icon[icon as IconName][tone as ToneName || 'graphite'] : null

const sidebar: Record<string, Array<Record<string, unknown>>> = {
    '/ref/': [
        { text: 'API', items: refPackages.map((p): SideItem => ({
            text: p.name,
            link: `/ref/${p.name}`,
            icon: preset(p.icon, p.tone) ?? Icon.code.danger,
        }))},
    ],
    '/': [
        {
            text: 'Docs',
            items: [
                { text: 'About', link: '/about', icon: Icon.info.muted },
                { text: 'License', link: '/license', icon: Icon.quotes.signal },
            ] as SideItem[],
        },
    ],
}

const anchorSlugify = (s: string) =>
  s.trim().replace(/ /g, '-').replace(/[^\w.\-]+/g, '')

export default defineConfig({
  title: site.title as string,
  description: site.description as string,
  base: (vp.base as string) || '/',
  srcDir: (vp.srcDir as string) || 'src',
  srcExclude: ['**/_partials/**'],
  outDir: OUT_DIR,
  cleanUrls: !!vp.cleanUrls,
  transformHtml,
  vite: {
    resolve: {
      alias: {
        '@': ROOT + '/',
        '@theme/': THEME_DIR + '/',
      },
    },
  },
  markdown: {
    anchor: { slugify: anchorSlugify },
  },
  themeConfig: {
    logo: tc.logo,
    search: tc.search as { provider: 'local' } | undefined,
    socialLinks,
    nav,
    docFooter: tc.docFooter,
    sidebar,
    footer,
  },
})
