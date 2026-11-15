# Portfolio hub — handoff notes (draft, not live)

Goal (owner's request): a main "overall portfolio" page that links to her two portfolios, plus design
improvements to both sites. Inspiration: Stripe (stripe.com/en-de), a Figma e-learning template (numbered
cards, arrow buttons, logo strip) and a Figma language-school template (rounded cards, floating chips).

## Done
- `hub-draft/index.html` + `paula.jpg`: finished draft of the hub (single file, no build step). Tested at
  1280px and 390px: no errors, no horizontal scroll. `preview-desktop.png` shows it.
- Links to https://paulamikki1-boop.github.io/Paula-Mikki-Seo-Portfolio/ and
  https://paulamikki1-boop.github.io/paula-tutor-profile/. All figures are taken from the two live sites.

## Update (later session)
- Mobile portrait fixed (capped at 340px, `preview-mobile.png`). Design review written up in `DESIGN-REVIEW.md` (not applied).
- Still needs the owner: create the `paulamikki1-boop.github.io` repo (item 1), choose a friendlier photo (item 2), and say which review items to apply.

## Not done / decisions for the owner
1. Where to host the hub. Recommended: a new repo named `paulamikki1-boop.github.io` (GitHub user site), so the
   hub is at https://paulamikki1-boop.github.io/ and both existing sites stay at their current URLs underneath.
   The owner must create that repo (the session could not); then copy index.html + paula.jpg into it.
2. Photo: the draft uses the ID-style headshot from the SEO repo; a friendlier photo would look better.
   Mobile: the portrait is too tall on phones; reduce it (e.g. max-height ~340px) or move it above the text.
3. Design review of the two sites was not yet written up or applied. Observations so far:
   - Tutor homepage: hero photo is small with the right half empty; About block is dense and repeats
     9A*/3A* three times; nav has 8 items; subject cards use mixed emoji icons; two result images in the
     gallery rendered blank in a full-page screenshot (check lazy-loading); no repeated "Book" CTA lower down.
   - SEO portfolio: strong content but ~9 000px long with 18 case-study cards (show top 4–6, then "show more");
     lots of small grey monospace text (#9CA3AF on white is low contrast); no CTA in the hero; footer still
     says "relocating to Germany, Oct 2026" (date has passed, confirm wording); no link back to a hub.
   - Both: different fonts/colours; add a shared "← Paula Mikki Tindoc" link back to the hub and bring the
     type and card styles closer (the hub uses DM Sans + DM Mono, navy/blue/green from both sites).
4. The SEO repo is cloned read-only in the session; attach it with push access before editing it.
