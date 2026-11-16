# Style: hub

The look of the portfolio hub, applied to all three sites in November 2026. Friendly and modern: light grey-blue
page, white rounded cards, one dark navy accent panel per page, bold tight headings, small monospace labels.
`hub-style.css` is the complete stylesheet of the tutor homepage in this style; start from it.

## Tokens

| Token | Value | Use |
| --- | --- | --- |
| `--navy` / `--ink` | `#0a1628` | headings, primary buttons, dark cards |
| `--blue` | `#1e3a5f` | eyebrow text |
| `--accent` | `#4a90d9` | bullets, gradient end |
| `--accent-deep` | `#2563eb` | kickers, links, gradient start |
| `--green` | `#0a7b5e` | gains, rank movement, "free notes" links, WhatsApp button |
| `--body` | `#46546a` | paragraph text |
| `--muted` | `#5d6b80` | captions, labels (do not go lighter: contrast) |
| `--line` | `#e1e7f0` | borders |
| `--bg` | `#f5f7fb` | page background |
| `--sky` / `--mint` | `#e8f0fe` / `#e3f5ee` | tinted fills (icon tiles, gain pills) |
| `--shadow` | `0 1px 2px rgba(10,22,40,.04), 0 12px 32px -12px rgba(10,22,40,.14)` | cards |

Fonts: **DM Sans** (400–700) for everything, **DM Mono** (400, 500) for kickers, eyebrows, tags and small data
labels. Load both from Google Fonts. The SEO portfolio also loads Noto Sans Thai for Thai queries.

Type: h1 `clamp(40px, 6–7vw, 68–80px)`, weight 700, letter-spacing `-.035em`, line-height about 1.04. h2
`clamp(28px, 3.6vw, 40px)`, weight 700, `-.025em`. Body 16px (lead 19px), line-height 1.6. Mono labels 12–12.5px,
uppercase, letter-spacing `.08em`.

Radius: buttons 12px (small 10px), chips and inputs 12–14px, strip 16px, fact cards 20px, feature cards 28px, big
panels 32px, pills 999px. Layout: `.wrap` max-width 1120px with 24px side padding; sections have 88px top padding
(64px on phones).

## Components

- **Backdrop**: `<div class="backdrop">` first in `<body>`; two blurred radial gradients (blue top right, green
  left) behind the hero. `body` needs `position: relative; overflow-x: hidden`.
- **Nav**: sticky, translucent page colour with blur. Brand = gradient square mark with "P" + name; a small
  "← Portfolio" link to the hub on the two sub-sites; text links; one small primary button as the last item.
  Under 860px the links collapse behind a Menu button (tutor site) or hide, leaving the brand and button.
- **Hero**: two columns (1.15fr / .85fr). Left: eyebrow pill with a green dot, h1 with one phrase in a gradient
  (`.g1` blue for teaching, `.g2` green for SEO), lead paragraph, primary + ghost buttons, optional stat row.
  Right: square photo in a white padded frame (28px radius) with two floating chips (`.chip-a` top left,
  `.chip-b` bottom right), each a bold figure over a short caption. On phones the photo goes above the text and
  the chips move to the frame's edges.
- **Strip**: white 16px-radius bar of mono labels under the hero (tools, exam boards).
- **Section head**: mono kicker, h2, and an optional short paragraph on the right.
- **Fact cards** (`.fact`): white, 20px radius, mono number `01`, h3, short text or a bulleted list. Grids of 3 or 4.
  A tinted `.fact-cta` card can close a grid with a button.
- **Feature cards** (`.card`): 28px radius, shadow, mono tag, large h3; `.card-dark` is the navy version with an
  arrow tile. Whole card is a link when it leads somewhere; it lifts 4px on hover.
- **Dark panel** (`.results`): navy 32px-radius block for proof (wins list plus image grid). One per page.
- **Contact panel** (`.contact`): navy-to-green diagonal gradient, 32px radius; heading and text on the left,
  translucent link rows or a white form card on the right. Always the last block before the footer.
- **Footer**: one quiet line, copyright left and cross-links to the other sites right.

## Do and don't

- Do keep green for gains and positive movement only, and blue for structure.
- Do use one dark panel and one gradient contact panel per page; more makes the page heavy.
- Do write real numbers in chips and stats, taken from the page's own content.
- Don't use serif headings, emoji as icons, or text lighter than `--muted` on a light background.
- Don't let the page scroll sideways at 390px; grids drop to one or two columns.
- Don't add drop shadows to elements inside a card; the card carries the shadow.
- Respect `prefers-reduced-motion` (the stylesheet already switches transitions off).
