# Validation record

Publication checks, 2026-10-30. Schema validation, generated views, local Markdown links and anchors, and offline regression tests passed locally. The public [Actions history](https://github.com/DmytroHuzz/awesome-diy-learning/actions) records hosted validation against the Python 3.11 and 3.13 matrix. All 124 resources remain present after removing private workspace references from the catalogue, generator and generated documentation.

## Metadata and generated documentation

- JSON Schema Draft 2020-12 validation and semantic editorial checks passed for 124 unique resources.
- All 131 original resource-table rows are accounted for exactly once; seven repeated rows were merged. All 53 controlled topics are represented across six categories, including the research queue.
- Eleven generated Markdown views are reproducible and checked for freshness. Local Markdown paths and anchors are checked without external requests.
- The offline regression suite contains 38 tests for data-loss prevention, URL aliases, invalid metadata, unsupported review claims, generation, local links, robots rules, redirects, rate limits and network failures.
- Local schema/test execution uses CPython 3.14.7 in the project virtual environment. The GitHub Actions matrix separately targets Python 3.11 and 3.13. Standard-library generation and link checks also ran with the host Python.

## Editorial inspection

23 resources have independent publisher evidence: 11 have representative instructions inspected at `sample-reviewed` level; the other 12 have source-level checks. The remaining 95 candidates and six reference-only entries are retained with explicit uncertainty. Nothing is marked build-tested.

Inspections used publisher pages and document extraction. A source check of a video page confirms the offering and visible access conditions; it does not mean the entire video was watched. External downloads, account flows and software installation were not automatically assumed to work. Individual record evidence explains the inspection scope.

## External links

The first automated pass checked all 124 migrated main URLs before the Exploratorium URL correction and the addition of direct project links. It made bounded GET requests, respected robots policy and used at least a one-second interval between requests to the same host. No catalogue entry was automatically changed or removed.

- 58 URLs had no advisory flags.
- 66 URLs were flagged for manual inspection. Flags include bot-block indicators, robots restrictions, HTTP errors and timeouts; several flags can apply to one URL.
- HTTP observations: 82 responses with status 200, 14 with 403, 11 with 429, two with 404, one with 402, and 14 skipped/uncompleted observations.
- The two 404 observations were Blender Guru's tutorial index and Miller's project-ideas path; both also showed bot-block indicators. They remain in the review queue, not the checked listings.
- Independently inspected publisher content can be readable through research extraction even when the automated client is blocked. A robots restriction or bot block is not a finding that a resource is broken or paid.

Full observations: [initial link report](../reports/link-check-2026-10-30.json) and [additional direct project links](../reports/project-links-2026-10-30.json). The latter covers ten newly introduced URLs: four had no advisory flags and six require manual inspection. Network observations do not establish completeness, free access or safety.

## Scope limits

Most sources remain candidates rather than checked recommendations. Numerical material costs and most durations are unknown. There is no hands-on completion evidence. Broad libraries span varying difficulty and risk. The catalogue records what was actually observed, including inherited research notes, and exposes unresolved fields as null.

The manual external-link workflow is deliberately separate from pull-request CI so temporary remote errors do not block unrelated contributions. It uploads a report and does not open issues, email creators, or edit the dataset.

## Private source references

Resource provenance and inherited evidence point to the public migration audit rather than a private workspace. The regression suite scans repository files for workspace URL patterns to prevent accidental reintroduction. Original tutorial links and creator credits are preserved.
