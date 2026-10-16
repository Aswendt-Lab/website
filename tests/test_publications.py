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
WORK = {'id': 'https://openalex.org/W1', 'doi': 'https://doi.org/10.1234/test', 'type': 'article', 'cited_by_count': 0, 'counts_by_year': [{'year': 2026, 'cited_by_count': 0}]}
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

    def test_duplicate_doi_keeps_richer_record(self):
        other = dict(WORK, id='https://openalex.org/W2', cited_by_count=5)
        self.assertEqual(u.select_works([WORK, other], CONFIG), [other])

    def test_preprint_and_journal_versions_remain_distinct(self):
        preprint = dict(WORK, id='https://openalex.org/W2', doi='https://doi.org/10.1234/preprint', type='preprint')
        self.assertEqual(len(u.select_works([WORK, preprint], CONFIG)), 2)

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
