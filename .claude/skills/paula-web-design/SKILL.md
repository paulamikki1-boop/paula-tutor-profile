---
name: paula-web-design
description: >-
  Design or redesign web pages for Paula's sites (the portfolio hub, the SEO portfolio, the tutor site and its notes,
  marking and shop pages) in one of her saved visual styles. Use this whenever Paula asks to design, redesign, restyle,
  refresh or "make it match" a page or site, to build a new page that should look like her other sites, or to add a
  new saved style. Currently one style is saved: "hub" (bold DM Sans headings, soft gradient backdrop, large rounded
  cards, floating stat chips), used on all three live sites.
---

# Paula web design

Paula has three static sites that share one look. This skill holds that look as a named style so any page can be
built or restyled to match, and so new styles can be added beside it later.

| Site | Repo | Live URL |
| --- | --- | --- |
| Portfolio hub | `paulamikki1-boop/paulamikki1-boop.github.io` | https://paulamikki1-boop.github.io/ |
| SEO portfolio | `paulamikki1-boop/Paula-Mikki-Seo-Portfolio` | https://paulamikki1-boop.github.io/Paula-Mikki-Seo-Portfolio/ |
| Tutor site | `paulamikki1-boop/paula-tutor-profile` | https://paulamikki1-boop.github.io/paula-tutor-profile/ |

All are plain HTML/CSS/JS on GitHub Pages with no build step. Each page carries its own `<style>` block.

## Styles

| Style | Spec | Stylesheet | Reference page |
| --- | --- | --- | --- |
| `hub` (default) | `styles/hub-style.md` | `styles/hub-style.css` | hub `index.html`; tutor `index.html` |

If Paula does not name a style, use `hub`. Read the style's spec before writing any markup.

## Workflow

1. **Read the page first.** List every piece of content on it: text, images, links, anchors (`id`s other pages or
   the nav link to), `<head>` meta tags, scripts. A redesign changes layout and styling, not content. Keep her
   wording unless she asks for copy changes, and tell her about any line you add or reword.
2. **Map content to the style's components** (hero, strip, section head, fact cards, feature cards, dark panel,
   contact panel). The spec lists them with the markup to use.
3. **Build.** Copy the style's stylesheet into the page's `<style>` block and add only the page-specific rules you
   need. For a very large page (the tutor homepage embeds its images as base64), script the rebuild so the images
   and head tags are carried over byte for byte instead of retyped.
4. **Keep what must not break:** the `<head>` SEO tags (title, description, canonical, Open Graph), every anchor id
   in use, relative internal links on the tutor site (it is served from a sub-path), and existing JavaScript hooks
   (class names and ids the scripts query).
5. **Test in a browser** at 1280px and 390px wide: no console errors, no horizontal scroll, every image loads, the
   mobile menu opens and closes, in-page links land on the right section. Look at the screenshots, do not rely on
   the checks alone. Floating chips must not cover a face.
6. **Show Paula screenshots** (desktop and phone) before anything goes live. When she approves, open a pull request
   to `main`; she merges it. Summarise in plain English what changed.

## Adding a new style

Create `styles/<name>.md` (tokens, components, do and don't) and `styles/<name>.css` (a complete stylesheet for one
reference page), add a row to the Styles table above, and mention the new style name in this file's description so
it can be found. Do not edit an existing style to make a new one; copy it.
