# License Policy

Default mode is prototype-broad. This allows the report to include assets that might be useful for internal prototyping, but release/commercial suitability must be explicit. A free price is not a license.

This is workflow guidance, not legal advice. Always verify current terms on the original asset page or official license page.

## License Buckets

### Release-Safe By Default

These can normally be recommended for production if the source page confirms the terms:

- CC0 / public domain.
- MIT, BSD, Apache-style permissive licenses for code-like assets or tools.
- CC-BY when attribution is acceptable and attribution text is captured.
- Marketplace royalty-free terms that explicitly allow use inside commercial games, provided redistribution restrictions are compatible with shipping the game.

### Usable With Conditions

These can be ranked, but must include notes:

- CC-BY: requires attribution.
- CC-BY-SA or other share-alike terms: may introduce distribution obligations; flag as risky unless the user accepts it.
- GPL/LGPL for art/audio/game assets: often unsuitable for closed-source games; flag before use.
- Mixamo/Adobe content: can be useful for characters/animations but may require account access and has service-specific restrictions.
- Asset packs that allow use in games but restrict resale/redistribution of raw source files.

### Prototype-Only Or Release Blocker

These may appear in reports only because the selected policy is prototype-broad:

- Non-commercial only.
- Personal-use only.
- Game jam only.
- Editorial-use only.
- No-derivatives when modifications, optimization, or format conversion are needed.
- Unknown commercial status.
- Author says "free" but license text is absent or ambiguous.
- Terms prohibit redistribution in a way that conflicts with bundling files in a shipped game.

Mark these as:

```text
verdict: prototype_only
release_blocker: true
```

### Reject

Reject and do not recommend:

- No license and no clear owner permission.
- Contradictory license terms.
- Ripped, extracted, or recreated copyrighted/franchise content.
- Branded models/logos intended to represent protected trademarks unless the user has rights.
- AI-scraped/repost pages where provenance cannot be traced to the creator.
- Malware-like downloads, password-protected archives from suspicious mirrors, or pages that require unsafe installers.

## Verification Rules

- Use the original creator page when possible.
- If a search result points to a mirror, follow it to the creator/source page.
- Record the exact license name and source URL.
- Capture attribution text for CC-BY or author-requested credit.
- If the page links a separate license document, open it and check compatibility.
- If the license varies inside the pack, treat the strictest relevant asset terms as the pack terms.
- If current terms are unclear, lower license/provenance score and do not recommend download.

## Attribution Record

For any downloaded asset, preserve:

```json
{
  "asset_name": "Example Asset",
  "author": "Author Name",
  "source_url": "https://example.com/asset",
  "license": "CC-BY 4.0",
  "license_url": "https://creativecommons.org/licenses/by/4.0/",
  "attribution_text": "Example Asset by Author Name, licensed CC-BY 4.0",
  "requires_attribution": true,
  "release_blocker": false
}
```

## User Confirmation Before Download

The first output is always a report. Download only after the user clearly chooses candidates by rank, name, or URL.

Acceptable approval:

- "Download rank 1 and 3."
- "Use the Kenney pack."
- "Download this URL: ..."

Not enough:

- "Looks good."
- "Find some assets."
- "What do you recommend?"

If approval is vague, ask which candidate to download.
