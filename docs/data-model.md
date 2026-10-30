# Data model

[data/resources.json](../data/resources.json) is the authoritative versioned catalogue. JSON avoids a YAML parser dependency, duplicate-key surprises and implicit dates/booleans. The top-level object contains `version: 1` and a `resources` array. [resource.schema.json](../schema/resource.schema.json) uses JSON Schema Draft 2020-12, forbids unknown keys and defines controlled vocabularies in `$defs`. The validator adds cross-field and identity rules.

Generated README/category pages, the taxonomy, full details, migration ledger and review queue are views, never a second editable resource database. Reports are dated observations, not an alternative source of catalogue facts. Additive fields require schema, documentation, generator and test updates; a breaking model change requires a version change and migration.

## Fields

| Field | Meaning |
| --- | --- |
| id | Stable lowercase hyphenated unique identity; retain when a title changes |
| title, url, creator, description | Human title, original/current publisher URL, original author/organization and concise original summary |
| primary_category | One of six broad categories; at least one topic must belong to it |
| topics, tags | Controlled multi-topic list; flexible lowercase hyphenated editorial tags |
| formats | One or more of article, video, pdf, patterns, interactive, course, project-library |
| approaches | One or more learner activities from the vocabulary below |
| difficulty | beginner, intermediate, advanced, varies, or null; scope to the representative project |
| free_access.status | open, free-registration, mixed, restricted-free-tier, unverified |
| free_access.details | What is actually free, optional payment and meaningful account/license limits |
| beginner_project_url | Direct representative starting-project URL or null; naming does not imply safe for all beginners |
| tools, materials | Supported string lists or null; an empty list means confirmed none |
| workspace | null or type plus details: tabletop, workbench, workshop, kitchen, outdoors, computer, varies |
| duration | null or minutes_min, minutes_max, details; distinguish video runtime, active work and elapsed project time |
| cost_band | none, low, medium, high, varies, or null; use only with explicit evidence and scope in notes |
| screen_time | minimal, mixed, digital, or null; editorial inference must be labeled |
| languages | BCP-47-style language tags for inspected content or null; no inferred translation claims |
| beginner_suitable | true, false or null for the specific scope; requires an assessed risk if true |
| safety | risk plus practical notes; risk is low, moderate, specialist-only, varies, or null |
| review.level | source-checked, sample-reviewed or build-tested; evidence rules apply |
| review.disposition | listed, needs-review, reference-only or excluded; distinct from review depth |
| review.last_verified | Independent publisher inspection date (YYYY-MM-DD) or null; never inferred from HTTP alone |
| review.evidence | URL, checked_on, kind (source/sample/build), notes; identify exactly what was inspected |
| editorial_notes | Caveats, scope, uncertainty, inference labels, corrections and rejection reasons |
| provenance | null for new submissions, or Notion source URL and every original occurrence |
| provenance.occurrences | Original row, section, title, URL, format/approach/setup text, requirements and notes |
| repair | null or the repair attributes below |
| featured | Explicit editorial selection for the README; must be listed, beginner-suitable and have a direct project link |

`null` is unknown, not zero, false, free or unnecessary. Do not turn source setup labels such as “Medium” into a cost claim. Cost bands have no universal currency thresholds; leave them null until the contributor documents what the band covers. Original URLs remain in provenance when a verified official replacement becomes `url`.

## Learning approaches

| Value | Learner activity |
| --- | --- |
| guided-build | Follow instructions to create a specific object |
| project-progression | Build increasingly complex projects in sequence |
| experimental-learning | Explore principles through controlled experiments |
| design-challenge | Solve a problem through independent design |
| pattern-or-plan | Construct from diagrams, dimensions or templates |
| repair-walkthrough | Diagnose and fix an existing object |
| teardown | Disassemble and understand a system |
| restoration | Return an old or damaged object to useful condition |
| upgrade-or-modification | Improve or repurpose an existing object |
| interactive-lab | Complete guided exercises in a digital environment |

A project library is a **format**, not a learning approach. A video may teach any approach. A course may have a guided build or an experimental sequence.

## Repair attributes

| Field | Values / purpose |
| --- | --- |
| object_type | A meaningful object description; exact model when applicable |
| activities | teardown, diagnosis, repair, restoration, upgrade, upcycling, maintenance |
| device_specificity | general-technique, product-family, exact-model, or null |
| replacement_parts | Supported parts list, empty for confirmed none, or null |
| reversibility | reversible, partly-reversible, destructive, or null |
| risk_level | Same value as safety.risk; null remains unknown |
| functional_checks | Specific post-repair checks or null; distinguish publisher directions and editorial suggestions |

## Identity and reproducibility

The URL comparator ignores HTTP/HTTPS, `www`, default ports, fragments, trailing slash and common tracking parameters, decodes unreserved escapes and sorts query parameters. It preserves path case, meaningful query values, ports and reserved escapes. This is a review heuristic: it never rewrites stored original URLs. Alias URLs in provenance participate in cross-record deduplication. Distinct tutorials on the same site remain distinct.

The generator sorts deterministically and emits no runtime timestamps. `--check` detects stale or orphaned generated category files. CI validates local relative Markdown paths and anchor targets. The network checker uses bounded GET reads, timeouts, per-host delays and robots rules; it flags cross-host/downgrade/login redirects, HTTP errors and possible access restrictions. Reports are advisory, and no entry is automatically removed.

## Future search and collections

The existing fields support subject, format, approach, difficulty, time, cost, workspace, screen use, language, access, beginner suitability and repair/construction filters. Multi-topic tags permit creative/technical overlap rather than forcing one binary label. Unknowns must remain filterable as unknowns. Collection ideas are documented in the [taxonomy](taxonomy.md); v1 intentionally consists of portable JSON and Markdown.
