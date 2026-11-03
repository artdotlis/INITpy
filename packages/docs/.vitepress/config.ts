// SPDX-FileCopyrightText: 2026 Artur Lissin
//
// SPDX-License-Identifier: Unlicense

import { DefaultTheme, defineConfig } from 'vitepress'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { resolve, dirname } from 'node:path'
import toml from 'toml'

const CONFIG_DIR = dirname(fileURLToPath(import.meta.url))
const ROOT = resolve(CONFIG_DIR, '..')
const THEME_DIR = resolve(CONFIG_DIR, 'theme')

const config = toml.parse(
  readFileSync(new URL('./config.toml', import.meta.url), 'utf-8')
) as {
  site?: Record<string, unknown>
  vitepress?: {
    base?: string
    cleanUrls?: boolean
    lastUpdated?: boolean
    srcDir?: string
    themeConfig?: {
      logo?: DefaultTheme.ThemeableImage
      search?: { provider: 'local' }
      socialLinks?: Array<{ icon: string; link: string }>
      nav?: Array<{ text: string; link: string }>
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

const anchorSlugify = (s: string) =>
  s.trim().replace(/ /g, '-').replace(/[^\w.\-]+/g, '')

export default defineConfig({
  title: site.title as string,
  description: site.description as string,
  base: (vp.base as string) || '/',
  srcDir: (vp.srcDir as string) || 'src',
  srcExclude: ['**/_partials/**'],
  outDir: fileURLToPath(new URL('../../../public/docs/', import.meta.url)),
  cleanUrls: !!vp.cleanUrls,
  lastUpdated: !!vp.lastUpdated,
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
    sidebar: {
      '/ref/': [
        { text: 'API Reference', items: [
          { text: 'Overview', link: '/ref/' },
          { text: 'scaffolder', link: '/ref/scaffolder' },
          { text: 'shared_utils', link: '/ref/shared_utils' },
        ]},
      ],
      '/': [
        { text: 'Docs', items: [
          { text: 'Home', link: '/' },
          { text: 'About', link: '/about/' },
          { text: 'License', link: '/license/' },
        ]},
      ],
    },
    footer,
  },
})
