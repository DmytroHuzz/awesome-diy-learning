# Contributing

Help someone find a project they can actually start. A careful correction or one excellent tutorial is more useful than a long list of unreviewed links.

## Suggest a resource

Use the [resource suggestion form](https://github.com/DmytroHuzz/awesome-diy-learning/issues/new?template=suggest-resource.yml). Include a direct free tutorial or a useful instructional collection, the original creator, something the learner will make or repair, access restrictions, required setup and any safety concerns. Disclose your affiliation. A commercial homepage alone is not enough.

Instruction must be actionable, credible, reproducible and self-paced. Paid supplies are allowed; mandatory paid instruction is not. A shop's useful free guide can qualify. A trial that expires before a learner can finish does not qualify as an unrestricted free resource. Do not submit copied or unauthorized reuploads. Read the [quality criteria](docs/quality-criteria.md).

## Edit the catalogue

1. Fork the repository and make a branch.
2. Edit **data/resources.json**. Find an existing source before adding a record; the same tutorial must not be duplicated under another topic. Keep the ID stable when a title changes.
3. Copy the structure of the real `origami-me` entry for an example, but replace its facts and evidence. Every field is documented in the [data model](docs/data-model.md). Use `null` for unknowns; an empty tools/parts list means confirmed none, not unknown.
4. Add one or more controlled topics and the approach that describes the learner's activity. Formats describe the medium separately. Add creator credit and a direct project URL when known. Use `provenance: null` for a new contribution; do not invent Notion occurrences.
5. Record publisher URLs, the actual inspection date and what was inspected under `review.evidence`. Use `source-checked` with `needs-review` for an unresolved candidate. Keep `free_access.status: unverified` until you check the real instruction. `last_verified` stays null until independent publisher evidence exists.
6. To promote to `listed`, confirm useful free instruction, access conditions and safety. `sample-reviewed` requires a complete representative-project inspection; `build-tested` additionally requires a real completion report. Never infer a build from a video, another person's claim or an automated link check.
7. For repairs, fill in the object and activity; unknown parts, reversibility and checks stay null. Label editorial functional-check suggestions as such. Exact-model repairs must identify the model and risks.
8. Run the commands below and commit the data plus generated Markdown. Do not edit generated pages directly.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/validate.py
python scripts/generate.py
python scripts/generate.py --check
python scripts/check_markdown.py
python -m unittest discover -s tests -v
```

Python 3.11+ is supported. Generation and link checking use only the standard library; JSON Schema validation uses the one direct dependency in requirements.txt. A working JSON example is the `origami-me` record in [the authoritative dataset](data/resources.json); its complete rendered metadata is [here](docs/catalogue-details.md#origami-me).

## Pull request checklist

- [ ] Direct free instruction, creator and access conditions are evidenced.
- [ ] No duplicate ID, canonical-equivalent URL or duplicated tutorial from a different topic.
- [ ] Unknown costs, time, language and equipment stay null.
- [ ] Format, approach, topics and review disposition are accurate.
- [ ] Safety notes and repair checks match the particular project.
- [ ] A review level is supported by dated evidence; no invented build testing.
- [ ] Schema, tests, Markdown links and generated-file checks pass.
- [ ] Changes to generated files come from the source data or generator.
- [ ] Third-party content has not been copied or relicensed; affiliations are disclosed.

## Broken links and disputed claims

Use the [broken-link form](https://github.com/DmytroHuzz/awesome-diy-learning/issues/new?template=broken-link.yml) with the resource ID, URL, date, observed error and any official replacement. An HTTP 403, CAPTCHA, geographic restriction or timeout is not proof the resource is gone. The link checker is advisory and never removes entries. Avoid repeated requests to a blocked server.

Use the [correction form](https://github.com/DmytroHuzz/awesome-diy-learning/issues/new?template=improve-resource.yml) to dispute a free-access claim, creator credit, description, setup or safety label. Link evidence and describe the smallest accurate correction. Maintainers can move a disputed entry to `needs-review` while investigating and retain excluded records with a reason. Creators are welcome to request corrections or removal of catalogue wording; no third-party tutorial is hosted here.

## Licensing and conduct

Contribute code under MIT and your original catalogue wording/metadata under CC0 1.0. Do not apply those terms to someone else's instructional work. See [licensing boundaries](docs/licensing.md) and the [Code of Conduct](CODE_OF_CONDUCT.md). This catalogue does not accept purchased rankings or undisclosed sponsored placement.
