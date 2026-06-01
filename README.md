# Comments reader

Reads customer comments from **Facebook** (Page post comments), **Gorgias**
(inbound customer messages), and **Judge.me** (product reviews), normalizes
them into one shape, and prints them newest-first (or as JSON).

## Where API keys live (and why)

**No keys are ever stored in this repo.** Every credential is read from an
environment variable at runtime — see [`.env.example`](.env.example) for the
full list of names.

- **Local runs:** copy `.env.example` to `.env` and fill in real values.
  `.env` is git-ignored, so it is never committed.
- **Claude Code on the web:** set the same variable names as
  environment variables / secrets in your environment settings
  (Environments → your environment). Those are not part of the repo.
  See https://code.claude.com/docs/en/claude-code-on-the-web

> ⚠️ Heads up: the gethookd token in `.mcp.json` is committed in plaintext
> and is in git history. Recommended fix: **rotate that token** in gethookd,
> then replace the literal value in `.mcp.json` with `${GETHOOKD_TOKEN}` and
> set `GETHOOKD_TOKEN` as an env var. (Left unchanged here pending your OK.)

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env        # then fill in your keys
```

## Usage

```bash
python -m comment_reader.main                      # all sources
python -m comment_reader.main --source gorgias     # one source
python -m comment_reader.main --source facebook --source judgeme --limit 50
python -m comment_reader.main --json > comments_export.json
```

Sources with missing credentials are skipped with a notice rather than
failing the whole run, so you can wire up one channel at a time.

## Getting each credential

| Source   | What you need | Where |
|----------|---------------|-------|
| Gorgias  | login email + API key, your subdomain | Settings → REST API |
| Judge.me | private API token + myshopify domain | Judge.me account → API |
| Facebook | Page access token (long-lived) + Page ID | Meta Graph API / Graph API Explorer |
