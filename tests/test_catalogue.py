"""Offline regression tests for data loss, unsupported claims and generation."""
import copy
import json
import re
import subprocess
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from catalogue import ROOT, SCHEMA, canonical_url, load, md
from validate import validate
from generate import render
from check_links import Checker, content_flags, public_url
from check_markdown import anchors, check


class CatalogueTests(unittest.TestCase):
    def setUp(self):
        self.data=load()
        self.schema=load(SCHEMA)
        self.first=self.data['resources'][0]

    def assertInvalid(self, needle):
        self.assertTrue(any(needle in e for e in validate(self.data,self.schema)), validate(self.data,self.schema))

    def test_real_dataset_passes(self):
        self.assertEqual([],validate(self.data,self.schema))

    def test_duplicate_id_fails(self):
        self.data['resources'][1]['id']=self.first['id']
        self.assertInvalid('duplicate ID')

    def test_canonical_duplicate_fails(self):
        self.data['resources'][1]['url']=self.first['url']+'?utm_source=test#intro'
        self.assertInvalid('canonical-equivalent')

    def test_alias_in_provenance_participates_in_deduplication(self):
        self.first['provenance']['occurrences'][0]['url']=self.data['resources'][1]['url']
        self.assertInvalid('canonical-equivalent')

    def test_unknown_topic_fails(self):
        self.first['topics']=['invented-topic']
        self.assertInvalid('topics')

    def test_unknown_approach_fails(self):
        self.first['approaches']=['project-library']
        self.assertInvalid('approaches')

    def test_required_field_fails(self):
        del self.first['creator']
        self.assertInvalid('required property')

    def test_unknown_field_fails(self):
        self.first['invented_score']=99
        self.assertInvalid('Additional properties')

    def test_build_test_requires_completion_evidence(self):
        self.first['review']['level']='build-tested'
        self.assertInvalid('real completion report')

    def test_sample_review_requires_complete_sample_evidence(self):
        self.first['review']['level']='sample-reviewed'
        self.first['review']['evidence']=[e for e in self.first['review']['evidence'] if e['kind']!='sample']
        self.assertInvalid('dated sample evidence')

    def test_unverified_cannot_be_listed(self):
        self.first['free_access']['status']='unverified'
        self.first['review']['disposition']='listed'
        self.assertInvalid('verified free access')

    def test_inherited_source_date_is_not_independent_verification(self):
        self.first['review']['evidence']=self.first['review']['evidence'][:1]
        self.assertInvalid('independent publisher evidence')

    def test_specialist_cannot_be_featured_as_beginner(self):
        self.first['beginner_suitable']=True
        self.first['safety']['risk']='specialist-only'
        self.assertInvalid('beginner suitability')

    def test_featured_requires_direct_project(self):
        self.first['featured']=True
        self.first['beginner_project_url']=None
        self.assertInvalid('featured resources')

    def test_duration_bounds(self):
        self.first['duration']={'minutes_min':30,'minutes_max':10,'details':'Invalid estimate'}
        self.assertInvalid('minimum exceeds')

    def test_dates_are_valid_calendar_dates(self):
        self.first['review']['evidence'][0]['checked_on']='2026-02-30'
        self.assertInvalid('date')

    def test_repair_risks_must_agree(self):
        repair=next(r for r in self.data['resources'] if r['repair'])
        repair['repair']['risk_level']='moderate' if repair['safety']['risk']!='moderate' else 'low'
        self.assertInvalid('risk must agree')

    def test_source_rows_not_assigned_twice(self):
        self.first['provenance']['occurrences'].append(copy.deepcopy(self.first['provenance']['occurrences'][0]))
        self.assertInvalid('assigned more than once')

    def test_initial_migration_has_every_row_exactly_once(self):
        rows=sorted(o['row'] for r in self.data['resources'] if r['provenance'] for o in r['provenance']['occurrences'])
        self.assertEqual(list(range(1,132)),rows)
        self.assertEqual(124,len([r for r in self.data['resources'] if r['provenance']]))

    def test_generated_views_are_current_and_order_independent(self):
        rendered=render(self.data,self.schema)
        reverse=copy.deepcopy(self.data)
        reverse['resources'].reverse()
        self.assertEqual(rendered,render(reverse,self.schema))
        for name,text in rendered.items():
            self.assertEqual(text,(ROOT/name).read_text(),name)

    def test_cross_topic_resource_appears_in_multiple_categories(self):
        r=next(r for r in self.data['resources'] if r['id']=='exploratorium-cardboard-automata')
        rendered=render(self.data,self.schema)
        for category in ['art-and-design','engineering-and-technology']:
            self.assertIn(r['title'],rendered[f'categories/{category}.md'])

    def test_reference_only_resources_never_enter_checked_tables(self):
        rendered=render(self.data,self.schema)
        for r in self.data['resources']:
            if r['review']['disposition']=='reference-only':
                for cat in self.schema['$defs']['category']['enum']:
                    table=rendered[f'categories/{cat}.md'].split('## Research and reference queue')[0]
                    self.assertNotIn(r['url'],table)

    def test_approach_docs_cover_schema_vocabulary(self):
        text=(ROOT/'docs/data-model.md').read_text()
        for value in self.schema['$defs']['approach']['enum']:
            self.assertIn('| '+value+' |',text)

    def test_local_markdown_links(self):
        self.assertEqual([],check())

    def test_repository_contains_no_private_workspace_links(self):
        pattern = re.compile(r'https?://(?:[\w-]+\.)?notion\.(?:com|so|site)(?=[/:?#\s])', re.I)
        paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
        matches = []
        for name in filter(None, paths):
            path = ROOT / name
            if path.is_file() and pattern.search(path.read_text(encoding='utf-8')):
                matches.append(name)
        self.assertEqual([], matches, 'Private workspace links must not be published: ' + ', '.join(matches))

    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'bad.json'
            path.write_text('{"id": 1, "id": 2}')
            with self.assertRaisesRegex(ValueError,'Duplicate JSON key'):
                load(path)


class URLTests(unittest.TestCase):
    def test_common_equivalences(self):
        self.assertEqual(canonical_url('http://WWW.Example.com:80/a/%7eb/?b=2&a=1&utm_source=x#x'),canonical_url('https://example.com/a/~b?a=1&b=2'))

    def test_meaningful_differences_remain(self):
        for left,right in [('https://a.com/A','https://a.com/a'),('https://a.com/?p=1','https://a.com/?p=2'),('https://a.com:8080/','https://a.com/'),('https://a.com/a%2Fb','https://a.com/a/b')]:
            self.assertNotEqual(canonical_url(left),canonical_url(right))

    def test_markdown_text_cannot_break_table(self):
        self.assertNotIn('|',md('A|B\n<C>'))
        self.assertIn('&lt;',md('<script>'))

    def test_anchor_duplicates(self):
        self.assertEqual({'hello','hello-1','manual'},anchors('# Hello\n# Hello\n<a id="manual"></a>'))

    def test_missing_local_target_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory,'README.md').write_text('[missing](docs/no.md)')
            self.assertIn('missing target',check(Path(directory))[0])


class LinkCheckerTests(unittest.TestCase):
    def test_access_heuristics_are_advisory(self):
        self.assertIn('possible-access-restriction',content_flags(b'<p>Subscribe to continue</p>','text/html'))
        self.assertEqual([],content_flags(b'Subscribe to continue','application/pdf'))
        self.assertEqual([],content_flags(b'<p>Free guide; optional paid course.</p>','text/html'))

    def test_private_and_invalid_targets_rejected(self):
        for url in ['file:///etc/passwd','https://user:password@example.com','http://127.0.0.1/','http://[::1]/']:
            self.assertFalse(public_url(url))

    def test_redirect_flag_and_target(self):
        checker=Checker()
        with patch('check_links.public_url',return_value=True), patch.object(checker,'allowed',return_value=(True,'')), patch.object(checker,'fetch',side_effect=[(302,{'Location':'https://other.example/login'},b''),(200,{'Content-Type':'text/html'},b'Sign in to continue')]):
            result=checker.check('https://example.org/project')
        self.assertEqual('manual-review',result['status'])
        self.assertIn('cross-host-redirect',result['flags'])
        self.assertIn('possible-paywall-or-login-redirect',result['flags'])
        self.assertEqual('https://other.example/login',result['final_url'])

    def test_robots_disallow_skips_content_fetch(self):
        checker=Checker()
        with patch('check_links.public_url',return_value=True),patch.object(checker,'allowed',return_value=(False,'robots-disallow')),patch.object(checker,'fetch') as fetch:
            result=checker.check('https://example.org/project')
        fetch.assert_not_called()
        self.assertIn('robots-disallow',result['flags'])

    def test_robots_policy_is_cached_per_origin(self):
        checker=Checker()
        with patch.object(checker,'fetch',return_value=(200,{},b'User-agent: *\nDisallow: /private')) as fetch:
            self.assertFalse(checker.allowed('https://example.org/private')[0])
            self.assertTrue(checker.allowed('https://example.org/public')[0])
            self.assertEqual(1,fetch.call_count)

    def test_network_failure_retains_record_as_manual_review(self):
        checker=Checker()
        with patch('check_links.public_url',return_value=True),patch.object(checker,'allowed',side_effect=TimeoutError('Timed out')):
            result=checker.check('https://example.org/project')
        self.assertIn('network-error-manual-review',result['flags'])
        self.assertEqual('https://example.org/project',result['url'])

    def test_rate_limit_sleeps_between_requests_to_one_host(self):
        checker=Checker(delay=1)
        class Response:
            status=200
            headers={}
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,size):return b'ok'
        with patch.object(checker.opener,'open',return_value=Response()),patch('check_links.time.monotonic',side_effect=[10,10,10.25,10.25]),patch('check_links.time.sleep') as sleep:
            checker.fetch('https://example.org/a')
            checker.fetch('https://example.org/b')
        sleep.assert_called_once_with(0.75)


if __name__=='__main__':unittest.main()
