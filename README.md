# Comments reader

Reads customer comments from **Facebook** (Page post comments), **Gorgias**
(inbound customer messages), and **Judge.me** (product reviews), normalizes
them into one shape, and prints them newest-first (or as JSON).

## Where API keys live (and why)

**No keys are ever stored in this repo, and they never touch a Claude Code
session.** Every credential is read from an environment variable at runtime,
and the only place those values exist is **GitHub Actions Secrets**. The
reader runs in CI (see [`.github/workflows/comments.yml`](.github/workflows/comments.yml)),
so the keys are never present in an interactive chat session.

### Setup (one time)

In GitHub: **Settings → Secrets and variables → Actions → New repository secret**,
and add each of these (see [`.env.example`](.env.example) for what each is):

| Secret | Source |
|--------|--------|
| `GORGIAS_DOMAIN`, `GORGIAS_EMAIL`, `GORGIAS_API_KEY` | Gorgias → Settings → REST API |
| `JUDGEME_API_TOKEN`, `JUDGEME_SHOP_DOMAIN` | Judge.me → API |
| `FACEBOOK_PAGE_ID`, `FACEBOOK_ACCESS_TOKEN` | Meta Graph API |
| `FACEBOOK_API_VERSION` *(optional)* | defaults to `v19.0` |

The workflow runs every 6 hours and can also be triggered manually
(**Actions → Customer comments → Run workflow**). Results are uploaded as a
`comments` JSON artifact on each run.

> **Why not store the keys in the Claude Code environment?** That would let
> the agent use them in sessions, but it also means the key *values* are
> reachable inside an interactive session. Keeping them in GitHub Actions
> Secrets only — and running in CI — guarantees they never appear in a chat.
> GitHub Actions Secrets are **not** readable by Claude Code web sessions, so
> the reader can't be run interactively here; that's the intended trade-off.

> **Local runs** (optional, your own machine): copy `.env.example` to `.env`
> and fill in values. `.env` is git-ignored.

> ℹ️ The `gethookd` token in `.mcp.json` is a separate concern — it's an MCP
> server used by Claude interactively, not part of this CI reader. It's still
> committed in plaintext there; consider rotating it.

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
