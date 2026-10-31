# Validation record

Editorial queue review and local verification, 2026-10-30. The catalogue retains all 124 resources and 131 original source rows. The [source review report](source-review.md) records decisions for all 101 records that previously formed the research/reference queue. Hosted validation runs automatically on push against Python 3.11 and 3.13; inspect the public [Actions history](https://github.com/DmytroHuzz/awesome-diy-learning/actions) for commit-specific results.

## Metadata, documentation and tests

- JSON Schema Draft 2020-12 and semantic editorial validation pass for 124 unique resources.
- All 131 original source rows remain accounted for exactly once, with seven merged repeats. All 53 supported topics remain represented across six categories, including reference and pending records.
- Twelve generated Markdown views are reproducible: README, six category pages, resource details, taxonomy, migration ledger, unresolved queue and source review report.
- The offline regression suite has 45 passing tests. Seven new tests cover complete original-queue audit coverage, audit evidence/dates, duplicate batches, unresolved attempts, and report/queue accounting. Existing tests cover schema and identity failures, unsupported review claims, generation, local links, private-source-link regression, robots policy, redirects, rate limiting and network failures.
- Local validation uses CPython 3.14.7 in the project virtual environment. Generation freshness and local Markdown path/anchor checks pass. CI separately targets Python 3.11 and 3.13.

## Editorial outcomes

The original queue had 95 candidates and six references. All **101** received an inspection or documented access attempt. Its current outcomes are **67 listed offerings**, **20 references**, and **14 unresolved candidates**; none was silently deleted or newly merged.

The complete catalogue now contains **90 listings**, **20 references**, and **14 unresolved candidates**. **29** resources have complete representative written instructions inspected at `sample-reviewed` level, including 18 newly reviewed samples. Nothing is marked `build-tested`. There are 115 records with independent publisher inspection dates; that includes source-level checks and readable references, and does not mean every complete lesson was reviewed. Access-only failures retain null verification dates.

Corrections include recovered Blender Guru and Miller URLs, Canon PRINT requirements, DMC account/newsletter delivery, Amigurumi sign-in versus paid PDFs, Onshape public-document restrictions, limited watchmaking samples, discontinued spectrograph-kit materials, and a laptop-cleaning power-isolation question. The [remaining queue](review-queue.md) gives each unresolved barrier rather than a generic unchecked label.

Inspections used publisher pages, document extraction, official-site search and a browser for script-rendered content. Sculpey’s complete ornament procedure and DMC’s actual download options were checked in the browser. No account was created, newsletter signup submitted, paid course bought, full video course watched or physical project built. An embedded video confirms the identified offering; it does not establish full playback or tutorial quality. Tools, parts, language and duration remain unknown unless supported.

## External link observations

The original automated reports remain historical observations, not the latest editorial verdict. The first pass checked 124 migrated main URLs before subsequent canonical-link corrections: 58 had no advisory flags and 66 were flagged. HTTP observations were 82 responses with status 200, 14 with 403, 11 with 429, two with 404, one with 402, and 14 skipped/uncompleted observations. The original Blender Guru and Miller paths with 404 observations now have recovered publisher replacements; original addresses remain in provenance.

Full observations: [initial link report](../reports/link-check-2026-10-30.json) and [initial additional project-link report](../reports/project-links-2026-10-30.json). The latter covered ten URLs, with four unflagged and six requiring inspection. These reports were not rewritten to imply a new full network scan. The current editorial evidence is in [the generated source review](source-review.md) and each record.

The checker uses bounded GET requests, reasonable timeouts, robots policy and at least a one-second per-host interval. A bot block, robots restriction, geographic barrier or timeout is not a finding that a tutorial is broken or paid. No resource is automatically removed, and temporary remote failures do not block pull-request CI. The manual network workflow uploads advisory reports without opening issues or contacting creators.

## Limits and privacy

A source-level listing identifies an offering and access conditions; it is not a complete project assessment. Many libraries still need a sample review, gated lesson content was not enrolled in, and video instructions were not watched end to end. Numeric costs and most durations remain unknown. Broad libraries span varying levels and hazards; exact-device procedures and load-bearing repairs need matching competence and safety checks.

Current resource provenance and inherited evidence point to the public migration audit. The regression suite scans tracked repository files for private workspace URL patterns. Original tutorial addresses and creator credits remain intact; no private research-page address is included in the published current files.
