# Deployment Notes

## Static Site

This site is deployed as a collection of static HTML files. No build step is required. All CSS and JS are inline within each HTML file.

## Directory Structure

```
/
├── resources/
│   ├── index.html                              — Resource hub (filterable card grid)
│   ├── _template-pdf.html                      — Template for PDF-primary resources
│   ├── _template-notes.html                    — Template for written notes resources
│   ├── igcse-chemistry-past-paper-technique/
│   │   └── index.html                          — Full resource page
│   ├── a-level-biology-key-definitions/
│   │   └── index.html                          — Stub (coming soon)
│   ├── igcse-physics-formula-sheet/
│   │   └── index.html                          — Stub (coming soon)
│   └── igcse-economics-essay-structure-guide/
│       └── index.html                          — Stub (coming soon)
├── assets/
│   └── resources/                              — PDF files go here as [slug].pdf
├── sitemap.xml
└── DEPLOY.md
```

## Email Capture Form Endpoint

The PDF template (`_template-pdf.html`) includes an optional email capture form that posts to `/api/send-resource`. This endpoint does not exist yet and must be wired up before the form will work. The direct PDF download link works independently of the form.

### Endpoint Specification

**URL:** `POST /api/send-resource`

**Request body** (JSON or form-encoded):

| Field           | Type   | Description                              |
|-----------------|--------|------------------------------------------|
| `name`          | string | The user's name                          |
| `contact`       | string | Email address or WhatsApp number         |
| `resource_slug` | string | Slug identifying which resource PDF      |

**Expected behaviour:**

1. Look up the PDF at `/assets/resources/{resource_slug}.pdf`
2. Send the PDF to the provided contact (email with attachment, or WhatsApp link)
3. Optionally store the contact for future resource update notifications
4. Return a success/error JSON response

### Implementation Options

Choose one of these approaches:

- **Netlify Functions:** Create `netlify/functions/send-resource.js`. Use Nodemailer or SendGrid to send the email. Set SMTP credentials as environment variables.
- **Formspree:** Replace the form action with your Formspree endpoint URL (`https://formspree.io/f/YOUR_FORM_ID`). Formspree handles delivery but does not attach the PDF — include the PDF download link in the auto-reply instead.
- **Google Apps Script:** Deploy a Web App that receives the POST, sends the PDF via Gmail, and logs the contact to a Google Sheet.
- **Custom API:** Deploy a serverless function (AWS Lambda, Vercel, Cloudflare Workers) that handles the POST, sends the email, and logs the contact.

### Environment Variables (if using Netlify Functions or custom API)

```
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASS=your-password
FROM_EMAIL=paula@yourdomain.com
SITE_URL=https://yourdomain.com
```

## Adding New Resources

1. Create a new folder under `/resources/` with the resource slug as the folder name.
2. Copy either `_template-pdf.html` or `_template-notes.html` into the folder as `index.html`.
3. Replace all `[placeholder]` values in the template.
4. If the resource has a PDF, place it at `/assets/resources/[slug].pdf`.
5. Add a card for the resource in `/resources/index.html` inside the `#cards-grid` div.
6. Add a `<url>` entry in `/sitemap.xml`.
7. Update the related resources blocks on other pages as appropriate.
