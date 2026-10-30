#!/usr/bin/env python3
"""Validate schema, identity, editorial evidence and cross-field invariants."""
import argparse
from datetime import date
import sys
from urllib.parse import urlsplit
from catalogue import DATA, SCHEMA, canonical_url, load
try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:
    sys.exit('Install the validator first: python -m pip install -r requirements.txt')


def validate(document, schema=None):
    schema = schema or load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    errors = []
    for error in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(document):
        path = '.'.join(map(str, error.absolute_path)) or '<root>'
        errors.append(f'{path}: {error.message}')
    if errors:
        return sorted(errors)
    ids, urls = {}, {}
    topic_categories = schema['x-topic-categories']
    provenance_rows = set()
    for index, resource in enumerate(document['resources']):
        rid = resource['id']
        if rid in ids:
            errors.append(f'{rid}: duplicate ID (rows {ids[rid]} and {index})')
        ids[rid] = index
        owned_urls = [resource['url']]
        if resource['provenance']:
            owned_urls += [o['url'] for o in resource['provenance']['occurrences']]
            for occurrence in resource['provenance']['occurrences']:
                key = (resource['provenance']['source'], occurrence['row'])
                if key in provenance_rows:
                    errors.append(f'{rid}: source row {key[1]} assigned more than once')
                provenance_rows.add(key)
        for url in set(owned_urls):
            try:
                key = canonical_url(url)
            except ValueError as error:
                errors.append(f'{rid}: malformed URL {url}: {error}')
                continue
            parsed = urlsplit(url)
            if not parsed.hostname or parsed.username or parsed.password or any(c in url for c in '\n\r<>'):
                errors.append(f'{rid}: URL must be an absolute HTTP(S) URL without credentials: {url}')
            if key in urls and urls[key] != rid:
                errors.append(f'{rid}: canonical-equivalent URL also belongs to {urls[key]}: {url}')
            urls[key] = rid
        if not any(topic_categories[t] == resource['primary_category'] for t in resource['topics']):
            errors.append(f'{rid}: at least one topic must belong to the primary category')
        if resource['featured'] and (resource['review']['disposition'] != 'listed' or resource['beginner_suitable'] is not True or not resource['beginner_project_url']):
            errors.append(f'{rid}: featured resources must be listed, beginner-suitable and directly linked')
        review = resource['review']
        kinds = {e['kind'] for e in review['evidence']}
        if review['level'] in ['sample-reviewed', 'build-tested']:
            if 'sample' not in kinds or not review['last_verified'] or not resource['beginner_project_url']:
                errors.append(f'{rid}: sample-reviewed/build-tested requires dated sample evidence and a representative project URL')
        if review['level'] == 'build-tested' and 'build' not in kinds:
            errors.append(f'{rid}: build-tested requires a real completion report in build evidence')
        if review['disposition'] == 'listed':
            if resource['free_access']['status'] == 'unverified' or not review['last_verified']:
                errors.append(f'{rid}: listed recommendations require verified free access and verification date')
        if resource['beginner_suitable'] is True and resource['safety']['risk'] in ['specialist-only', 'varies', None]:
            errors.append(f'{rid}: beginner suitability requires an assessed low or moderate risk')
        for evidence in review['evidence']:
            if date.fromisoformat(evidence['checked_on']) > date.today():
                errors.append(f'{rid}: evidence date cannot be in the future')
        if review['last_verified'] and review['last_verified'] not in {e['checked_on'] for e in review['evidence'] if e['url'] != (resource['provenance'] or {}).get('source')}:
            errors.append(f'{rid}: verification date must match independent publisher evidence')
        duration = resource['duration']
        if duration and duration['minutes_min'] and duration['minutes_max'] and duration['minutes_min'] > duration['minutes_max']:
            errors.append(f'{rid}: duration minimum exceeds maximum')
        repair = resource['repair']
        if resource['primary_category'] == 'repair-and-restoration' and repair is None:
            errors.append(f'{rid}: repair category requires repair attributes')
        if repair and repair['risk_level'] != resource['safety']['risk']:
            errors.append(f'{rid}: repair risk and safety risk must agree')
    return sorted(set(errors))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('data', nargs='?', default=DATA)
    args = parser.parse_args()
    try:
        document = load(args.data)
        errors = validate(document)
    except (OSError, ValueError) as error:
        sys.exit(f'Cannot read catalogue: {error}')
    if errors:
        print('\n'.join('- ' + error for error in errors), file=sys.stderr)
        return 1
    print(f'Valid: {len(document["resources"])} unique resources; schema and editorial rules passed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
