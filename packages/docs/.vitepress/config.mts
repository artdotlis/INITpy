import { defineConfig } from 'vitepress'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import toml from 'toml'

const config = toml.parse(
  readFileSync(new URL('./config.toml', import.meta.url), 'utf-8')
)

const site = config.site || {}
const vp = config.vitepress || {}
// themeConfig lives under `vitepress.themeConfig` (nested), not a flat key.
const tc = vp.themeConfig || {}
const nav = tc.nav || []
const socialLinks = tc.socialLinks || []
const footer = Array.isArray(tc.footer) ? tc.footer[0] || {} : tc.footer || {}

// griffe2md renders headings/links that keep dots and case (e.g. `#scaffolder.main`);
// keep VitePress anchor ids in sync so those links resolve.
const anchorSlugify = (s: string) =>
  s.trim().replace(/ /g, '-').replace(/[^\w.\-]+/g, '')

export default defineConfig({
  title: site.title,
  description: site.description,
  base: (vp.base as string) || '/',
  srcDir: (vp.srcDir as string) || '.',
  srcExclude: ['**/_partials/**'],
  outDir: fileURLToPath(new URL('../../../public/docs/', import.meta.url)),
  cleanUrls: !!vp.cleanUrls,
  lastUpdated: !!vp.lastUpdated,
  markdown: {
    ...vp.markdown,
    anchor: { slugify: anchorSlugify },
  },
  themeConfig: {
    logo: tc.logo,
    search: tc.search,
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
