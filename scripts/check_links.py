#!/usr/bin/env python3
"""Polite, advisory link checking. Never edits or deletes catalogue entries."""
import argparse
from datetime import datetime, timezone
import ipaddress
import json
from pathlib import Path
import re
import socket
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from urllib.robotparser import RobotFileParser
from catalogue import DATA, ROOT, load

USER_AGENT = 'AwesomeDIYLearning-LinkCheck/1.0'
MAX_BYTES = 262144


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def public_url(url):
    """Do not let contributed URLs turn CI into a private-network scanner."""
    parts = urlsplit(url)
    if parts.scheme not in ['http', 'https'] or not parts.hostname or parts.username or parts.password:
        return False
    try:
        return all(ipaddress.ip_address(info[4][0]).is_global for info in socket.getaddrinfo(parts.hostname, parts.port or (443 if parts.scheme == 'https' else 80)))
    except (OSError, ValueError):
        return False


def content_flags(body, content_type):
    if 'html' not in content_type:
        return []
    text = re.sub(r'<[^>]*>', ' ', body.decode('utf-8', errors='replace')).lower()
    flags = []
    if re.search(r'subscribe to (?:continue|read)|purchase (?:this|the) course|paid membership required|sign in to continue', text):
        flags.append('possible-access-restriction')
    if re.search(r'verify (?:that )?you are human|access denied|checking your browser|captcha', text):
        flags.append('possible-bot-block')
    if re.search(r'<title[^>]*>\s*(?:404|page not found|not found)', body.decode('utf-8', errors='replace'), re.I):
        flags.append('possible-soft-404')
    return flags


class Checker:
    def __init__(self, timeout=12, delay=1.0):
        self.timeout, self.delay = timeout, delay
        self.opener = build_opener(NoRedirect())
        self.last_request = {}
        self.robots = {}

    def fetch(self, url):
        host = urlsplit(url).netloc
        wait = self.delay - (time.monotonic() - self.last_request.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        self.last_request[host] = time.monotonic()
        req = Request(url, headers={'User-Agent': USER_AGENT, 'Accept': 'text/html,application/pdf;q=0.9,*/*;q=0.5'})
        try:
            response = self.opener.open(req, timeout=self.timeout)
        except HTTPError as error:
            response = error
        with response:
            return response.status, dict(response.headers), response.read(MAX_BYTES)

    def allowed(self, url):
        parts = urlsplit(url)
        origin = parts.scheme + '://' + parts.netloc
        if origin not in self.robots:
            status, headers, body = self.fetch(origin + '/robots.txt')
            # A redirect, rate limit or server error leaves policy uncertain: skip.
            if status in [401, 403] or status == 429 or status >= 500 or 300 <= status < 400:
                self.robots[origin] = None
            else:
                robot = RobotFileParser()
                robot.parse(body.decode('utf-8', errors='replace').splitlines() if status == 200 else [])
                self.robots[origin] = robot
        robot = self.robots[origin]
        if robot is None:
            return False, 'robots-unavailable-or-restricted'
        crawl_delay = robot.crawl_delay(USER_AGENT) or robot.crawl_delay('*')
        if crawl_delay and crawl_delay > 60:
            return False, 'robots-long-crawl-delay'
        if crawl_delay:
            host = parts.netloc
            wait = crawl_delay - (time.monotonic() - self.last_request.get(host, 0))
            if wait > 0:
                time.sleep(wait)
        return robot.can_fetch(USER_AGENT, url), 'robots-disallow'

    def check(self, url):
        result = {'url': url, 'final_url': url, 'http_status': None, 'flags': [], 'redirects': []}
        current = url
        try:
            for _ in range(6):
                if not public_url(current):
                    result['flags'].append('unresolvable-or-nonpublic-host')
                    break
                allowed, reason = self.allowed(current)
                if not allowed:
                    result['flags'].append(reason)
                    break
                status, headers, body = self.fetch(current)
                headers = {k.lower(): v for k, v in headers.items()}
                result['http_status'] = status
                result['final_url'] = current
                if status in [301, 302, 303, 307, 308] and headers.get('location'):
                    target = urljoin(current, headers['location'])
                    result['redirects'].append({'from': current, 'to': target, 'status': status})
                    if urlsplit(current).hostname != urlsplit(target).hostname:
                        result['flags'].append('cross-host-redirect')
                    if urlsplit(current).scheme == 'https' and urlsplit(target).scheme == 'http':
                        result['flags'].append('https-downgrade')
                    if any(x in urlsplit(target).path.lower() for x in ['/login', '/signin', '/subscribe', '/pricing']):
                        result['flags'].append('possible-paywall-or-login-redirect')
                    current = target
                    continue
                result['content_type'] = headers.get('content-type', '')
                if not 200 <= status < 300:
                    result['flags'].append('http-error-manual-review')
                result['flags'] += content_flags(body, result['content_type'])
                break
            else:
                result['flags'].append('redirect-limit')
        except (OSError, URLError, ValueError, TimeoutError) as error:
            result['flags'].append('network-error-manual-review')
            result['error'] = str(error)
        result['flags'] = sorted(set(result['flags']))
        result['status'] = 'manual-review' if result['flags'] else 'reachable'
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=DATA)
    parser.add_argument('--output', type=Path, default=ROOT / 'reports/link-check.latest.json')
    parser.add_argument('--timeout', type=float, default=12)
    parser.add_argument('--delay', type=float, default=1.0)
    parser.add_argument('--limit', type=int)
    parser.add_argument('--id', action='append', dest='ids')
    args = parser.parse_args()
    if not 0 < args.timeout <= 60 or args.delay < 1 or (args.limit is not None and args.limit < 1):
        parser.error('timeout must be 0–60 seconds, delay at least 1 second, limit positive')
    resources = load(args.data)['resources']
    if args.ids:
        known = {r['id'] for r in resources}
        unknown = set(args.ids) - known
        if unknown:
            parser.error('unknown IDs: ' + ', '.join(sorted(unknown)))
        resources = [r for r in resources if r['id'] in args.ids]
    urls = list(dict.fromkeys(url for r in resources for url in [r['url'], r['beginner_project_url']] if url))
    if args.limit:
        urls = urls[:args.limit]
    checker = Checker(args.timeout, args.delay)
    results = []
    for index, url in enumerate(urls, 1):
        result = checker.check(url)
        results.append(result)
        print(f'{index}/{len(urls)} {result["status"]}: {url}', flush=True)
    report = {'checked_at': datetime.now(timezone.utc).isoformat(), 'user_agent': USER_AGENT,
              'policy': 'Advisory only; robots respected; one request per host per second; no automatic removals.', 'results': results}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'{len(results)} URLs checked; {sum(bool(r["flags"]) for r in results)} need manual inspection. Report: {args.output}')
    return 0  # External availability never breaks contributor CI.


if __name__ == '__main__':
    sys.exit(main())
