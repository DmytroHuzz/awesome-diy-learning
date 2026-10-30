"""Shared, deterministic catalogue helpers (standard library only)."""
import json
import re
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/resources.json'
SCHEMA = ROOT / 'schema/resource.schema.json'


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def load(path=DATA):
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=reject_duplicate_keys)


def label(value):
    return value.replace('-', ' ').capitalize() if value else 'Unknown'


def canonical_url(url):
    """Compare common aliases; preserve path case and meaningful query data.

    HTTP/HTTPS, www, default ports, fragments, trailing slash and tracking
    parameters are ignored. Reserved percent-escapes remain significant.
    This is a duplicate heuristic, never permission to rewrite a source URL.
    """
    parts = urlsplit(url)
    host = (parts.hostname or '').lower().removeprefix('www.')
    port = parts.port
    if port and (parts.scheme.lower(), port) not in [('http', 80), ('https', 443)]:
        host += ':' + str(port)
    unreserved = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~'
    def decode(match):
        char = chr(int(match[0][1:], 16))
        return char if char in unreserved else match[0].upper()
    path = re.sub(r'%[0-9A-Fa-f]{2}', decode, parts.path).rstrip('/')
    query = sorted((k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
                   if not k.lower().startswith('utm_')
                   and k.lower() not in {'fbclid', 'gclid', 'mc_cid', 'mc_eid'})
    return urlunsplit(('https', host, path, urlencode(query), ''))


def md(value):
    """Escape text in Markdown table cells; URLs are rendered separately."""
    return str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('|', '&#124;').replace('\n', ' ').replace('[', '\\[').replace(']', '\\]')
