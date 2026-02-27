# WEB_RETRIEVAL_REPORT

Date: February 27, 2026

## Module

Implemented module: `uniguru/retrieval/web_retriever.py`

Capabilities implemented:
1. Fetch webpage (`fetch_page`)
2. Extract text (`_extract_text` using BeautifulSoup or regex fallback)
3. Verify domain allowlist (`is_allowed_domain`)
4. Pass source to SourceVerifier (`verify_source`)
5. Refuse if unverifiable

## Domain controls

Allowlist includes:
- `.org`, `.edu`, `.gov`
- `sacred-texts.com`, `britannica.com`, `baps.org`, `swaminarayan.org`, `jainfoundation.in`, `jainworld.com`, and other trusted domains

Blocked patterns include:
- blogs/forums/social sources (e.g. `reddit`, `quora`, `x.com`, `medium.com`)

## Truth declaration behavior

- VERIFIED -> `Based on verified source: [source]`
- PARTIAL -> `This information is partially verified from: [source]`
- UNVERIFIED -> `I cannot verify this information from current knowledge.`

No unverifiable web content is returned as a confident answer.
