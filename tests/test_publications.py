import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/update_publications.py'
spec = importlib.util.spec_from_file_location('updater', SCRIPT)
u = importlib.util.module_from_spec(spec)
spec.loader.exec_module(u)
CONFIG = {'author_id': 'A1', 'orcid': '0000-0000-0000-0001', 'author_name': 'Test Author', 'include_types': ['article', 'review', 'preprint']}
WORK = {'id': 'https://openalex.org/W1', 'doi': 'https://doi.org/10.1234/test', 'type': 'article', 'cited_by_count': 0, 'counts_by_year': [{'year': 2026, 'cited_by_count': 0}], 'primary_location': {'source': {'type': 'journal', 'display_name': 'Test Journal'}}}
ROW = {'openalex_id': WORK['id'], 'title': 'A study', 'authors': 'Author T', 'year': '2026', 'publication_date': '2026-01-01', 'journal': 'Test Journal', 'doi': '10.1234/test', 'cited_by_count': '0'}


class PaginationTests(unittest.TestCase):
    def test_multiple_pages_include_zero_citation_work(self):
        other = dict(WORK, id='https://openalex.org/W2')
        pages = iter([
            {'meta': {'count': 2, 'next_cursor': 'next'}, 'results': [WORK]},
            {'meta': {'count': 2, 'next_cursor': None}, 'results': [other]},
        ])
        self.assertEqual(len(u.fetch_all('test', lambda *args: next(pages))), 2)

    def test_truncated_response_is_rejected(self):
        page = {'meta': {'count': 2, 'next_cursor': None}, 'results': [WORK]}
        with self.assertRaises(ValueError):
            u.fetch_all('test', lambda *args: page)

    def test_failed_response_is_not_an_empty_list(self):
        with self.assertRaises(ValueError):
            u.fetch_all('test', lambda *args: {})

    def test_duplicate_ids_are_rejected(self):
        page = {'meta': {'count': 2}, 'results': [WORK, WORK]}
        with self.assertRaises(ValueError):
            u.fetch_all('test', lambda *args: page)

    def test_zero_results_are_valid_for_uncited_work(self):
        self.assertEqual(u.fetch_all('test', lambda *args: {'meta': {'count': 0}, 'results': []}), [])


class DatasetTests(unittest.TestCase):
    def test_zero_citations_and_publication_metadata_survive(self):
        data = u.build_dataset([ROW], [WORK], CONFIG)
        self.assertEqual(data['publication_count'], 1)
        self.assertEqual(data['citation_count'], 0)
        self.assertEqual(data['publications'][0]['url'], 'https://doi.org/10.1234/test')
        self.assertEqual(data['annual_citations'][0]['width'], 0)

    def test_pmid_survives_pandas_float_conversion(self):
        self.assertEqual(u.normalize_pmid(12345678.0), '12345678')
        self.assertEqual(u.normalize_pmid('12345678.0'), '12345678')
        self.assertEqual(u.normalize_pmid('https://pubmed.ncbi.nlm.nih.gov/12345678/'), '12345678')
        self.assertEqual(u.normalize_pmid(float('nan')), '')

    def test_missing_csv_row_is_rejected(self):
        with self.assertRaises(ValueError):
            u.build_dataset([], [WORK], CONFIG)

    def test_csv_schema_change_is_rejected(self):
        with self.assertRaises(ValueError):
            u.build_dataset([{'openalex_id': WORK['id']}], [WORK], CONFIG)

    def test_mismatched_csv_citations_are_rejected(self):
        with self.assertRaises(ValueError):
            u.build_dataset([dict(ROW, cited_by_count='10')], [WORK], CONFIG)

    def test_wrong_author_orcid_is_rejected(self):
        with self.assertRaises(ValueError):
            u.verify_author(CONFIG, {'id': 'https://openalex.org/A1', 'orcid': 'wrong'})

    def test_duplicate_doi_is_kept_in_csv_but_counted_once(self):
        other = dict(WORK, id='https://openalex.org/W2', cited_by_count=5)
        self.assertEqual(len(u.select_works([WORK, other], CONFIG)), 2)
        rows = [ROW, dict(ROW, openalex_id=other['id'], cited_by_count='5')]
        data = u.build_dataset(rows, [WORK, other], CONFIG)
        self.assertEqual(data['total_record_count'], 2)
        self.assertEqual(data['publication_count'], 1)
        self.assertEqual(data['publications'][0]['cited_by_count'], 5)

    def test_preprint_and_journal_versions_remain_distinct(self):
        preprint = dict(WORK, id='https://openalex.org/W2', doi='https://doi.org/10.1234/preprint', type='preprint')
        self.assertEqual(len(u.select_works([WORK, preprint], CONFIG)), 2)

    def test_preprint_remains_exported_but_not_displayed_or_counted(self):
        preprint = dict(WORK, id='https://openalex.org/W2', type='preprint', doi='https://doi.org/10.1234/preprint', cited_by_count=9)
        rows = [ROW, dict(ROW, openalex_id=preprint['id'], doi='10.1234/preprint', cited_by_count='9')]
        data = u.build_dataset(rows, [WORK, preprint], CONFIG)
        self.assertEqual(data['total_record_count'], 2)
        self.assertEqual(data['publication_count'], 1)
        self.assertEqual(data['citation_count'], 0)
        self.assertEqual(len(data['all_publications']), 2)

    def test_biorxiv_mislabeled_article_is_not_displayed(self):
        work = dict(WORK, primary_location={'source': {'type': 'journal', 'display_name': 'bioRxiv'}})
        self.assertFalse(u.is_display_publication(work, CONFIG))

    def test_conference_abstract_and_mislabeled_presentation_are_excluded(self):
        for work in [dict(WORK, type='conference-abstract'), dict(WORK, title='P 18. A conference poster'), dict(WORK, title='FV 13 A conference talk'), dict(WORK, primary_location={'source': {'type': 'journal'}, 'raw_type': 'proceedings-article'})]:
            with self.subTest(work=work):
                self.assertFalse(u.is_display_publication(work, CONFIG))

    def test_repository_article_is_not_a_journal_publication(self):
        self.assertFalse(u.is_display_publication(dict(WORK, primary_location={'source': {'type': 'repository'}}), CONFIG))

    def test_data_paper_in_journal_is_included(self):
        self.assertTrue(u.is_display_publication(dict(WORK, type='data-paper'), CONFIG))

    def test_explicit_conference_exclusion_only_affects_display(self):
        config = dict(CONFIG, exclude_ids=[WORK['id']])
        data = u.build_dataset([ROW], [WORK], config)
        self.assertEqual(data['total_record_count'], 1)
        self.assertEqual(data['publication_count'], 0)
        self.assertEqual(data['publications'], [])

    def test_book_chapter_remains_a_publication(self):
        work = dict(WORK, type='book-chapter', primary_location={'source': {'type': 'book series'}})
        self.assertTrue(u.is_display_publication(work, CONFIG))

    def test_duplicate_title_with_archive_doi_is_counted_once(self):
        other = dict(WORK, id='https://openalex.org/W2', doi='https://doi.org/10.1234/archive')
        title = 'Longitudinal network changes during recovery after experimental stroke'
        rows = [dict(ROW, title=title, volume='12'), dict(ROW, title=title, openalex_id=other['id'], doi='10.1234/archive', volume='')]
        data = u.build_dataset(rows, [WORK, other], CONFIG)
        self.assertEqual(data['total_record_count'], 2)
        self.assertEqual(data['publication_count'], 1)
        self.assertEqual(data['publications'][0]['doi'], '10.1234/test')

    def test_jove_video_is_not_an_additional_publication(self):
        article = dict(WORK, doi='https://doi.org/10.3791/50802')
        video = dict(WORK, id='https://openalex.org/W2', doi='https://doi.org/10.3791/50802-v')
        rows = [dict(ROW, doi='10.3791/50802'), dict(ROW, openalex_id=video['id'], doi='10.3791/50802-v')]
        data = u.build_dataset(rows, [article, video], CONFIG)
        self.assertEqual(data['total_record_count'], 2)
        self.assertEqual(data['publication_count'], 1)
        self.assertEqual(data['publications'][0]['doi'], '10.3791/50802')

    def test_large_drop_keeps_previous_snapshot(self):
        previous = {'publications': [{'openalex_id': 'https://openalex.org/W' + str(i)} for i in range(20)]}
        with self.assertRaises(ValueError):
            u.build_dataset([ROW], [WORK], CONFIG, previous)

    def test_report_failure_does_not_replace_files(self):
        import json
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'scripts').mkdir()
            (root / '_data').mkdir()
            (root / 'scripts/publications-config.json').write_text(json.dumps(CONFIG))
            target = root / '_data/publications.json'
            target.write_text('{"publications": []}')
            before = target.read_bytes()
            with patch.object(u, 'refresh', side_effect=RuntimeError('API failed')):
                with patch('sys.argv', ['update_publications.py', '--root', directory]):
                    with self.assertRaises(RuntimeError):
                        u.main()
            self.assertEqual(target.read_bytes(), before)
            self.assertFalse((root / 'pdf/citations-latest.pdf').exists())


if __name__ == '__main__':
    unittest.main()


class OpenAccessTests(unittest.TestCase):
    def test_open_access_metadata_and_missing_values(self):
        for access, expected in [({'is_oa': True, 'oa_status': 'green', 'oa_url': 'https://example.org/paper.pdf'}, True),
                                 ({'is_oa': False, 'oa_status': 'closed'}, False), (None, False)]:
            with self.subTest(access=access):
                work = dict(WORK, open_access=access)
                record = u.build_dataset([ROW], [work], CONFIG)['publications'][0]
                self.assertEqual(record['is_open_access'], expected)
                self.assertEqual(record['open_access_url'], (access or {}).get('oa_url', ''))

    def test_unsafe_oa_url_is_not_published(self):
        work = dict(WORK, open_access={'is_oa': True, 'oa_url': 'javascript:alert(1)'})
        record = u.build_dataset([ROW], [work], CONFIG)['publications'][0]
        self.assertTrue(record['is_open_access'])
        self.assertEqual(record['open_access_url'], '')
