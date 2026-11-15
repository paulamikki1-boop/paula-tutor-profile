# Design review — both sites (recommendations, not yet applied)

Applying these means editing the two live sites, so nothing here has been changed. Say which to go ahead with.

## Tutor site (paula-tutor-profile)
1. **Hero**: photo is small with the right half empty. Enlarge the photo or add a short credentials/results card beside it.
2. **About**: dense, and "9A*/3A*" appears three times. Say it once in a stat row, keep the paragraph for story.
3. **Nav**: 8 items. Group into Notes, Shop, Marking, Contact, plus one "Book" button.
4. **Subject cards**: mixed emoji icons look uneven. Use one consistent line-icon set, or numbered cards like the hub.
5. **Gallery**: two result images rendered blank in a full-page screenshot. Check `loading="lazy"` (likely only a screenshot artefact, but verify in a real scroll).
6. **CTA**: no "Book a trial" button below the hero. Add one after About and one before the footer.

## SEO portfolio (Paula-Mikki-Seo-Portfolio)
1. **Length**: ~9,000px with 18 case-study cards. Show the top 4–6, then a "Show more" button.
2. **Contrast**: small grey mono text (#9CA3AF on white) fails WCAG AA. Use at least #6B7280 (about 4.8:1).
3. **Hero**: no call to action. Add "Get in touch" and "See case studies".
4. **Footer**: still says "relocating to Germany, Oct 2026", and that date has passed. Owner to confirm the new wording.

## Both
- Add a shared "← Paula Mikki Tindoc" link back to the hub.
- Align type and cards with the hub (DM Sans + DM Mono, navy/blue/green, rounded cards). The tutor site's Cormorant Garamond headings are the main difference.
- Note: the repo's CLAUDE.md says changes go to `main` through a PR after browser testing. Tutor-site edits should follow that.
