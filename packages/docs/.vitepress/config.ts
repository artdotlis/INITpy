// SPDX-FileCopyrightText: 2026 Artur Lissin
//
// SPDX-License-Identifier: Unlicense

import { defineConfig } from 'vitepress'
import { readFileSync } from 'node:fs'
import toml from 'toml'

const config = toml.parse(
  readFileSync(new URL('./config.toml', import.meta.url), 'utf-8')
)

const site = config.site || {}
const vp = config.vitepress || {}
const tc = config['vitepress.themeConfig'] || {}
const nav = tc.nav || []
const socialLinks = tc.socialLinks || []
const footer = Array.isArray(tc.footer) ? tc.footer[0] || {} : tc.footer || {}

export default defineConfig({
  title: site.title,
  description: site.description,
  base: (vp.base as string) || '/',
  outDir: (vp.outDir as string) || 'dist',
  cleanUrls: !!vp.cleanUrls,
  lastUpdated: !!vp.lastUpdated,
  markdown: vp.markdown,
  themeConfig: {
    logo: tc.logo,
    search: tc.search,
    socialLinks,
    nav,
    sidebar: {
      '/': [
        { text: 'Docs', items: [
          { text: 'Home', link: '/' },
          { text: 'About', link: '/about/' },
          { text: 'License', link: '/license/' },
        ]},
      ],
      '/api/': [
        { text: 'API Reference', items: [
          { text: 'scaffolder', link: '/api/scaffolder/' },
          { text: 'shared_utils', link: '/api/shared_utils/' },
        ]},
      ],
    },
    footer,
  },
})
