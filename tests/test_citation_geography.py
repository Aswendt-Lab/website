"""Exercise empty, unknown-only, and multi-country map inputs offline."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

import pandas as pd
from PIL import Image

MODULE = Path(__file__).resolve().parents[1] / 'scripts/citation_geography.py'
spec = importlib.util.spec_from_file_location('geography', MODULE)
geography = importlib.util.module_from_spec(spec)
spec.loader.exec_module(geography)


class GeographyTests(unittest.TestCase):
    def test_empty_citations_do_not_create_chart(self):
        with tempfile.TemporaryDirectory() as directory:
            result = geography.plot_citation_geography(
                pd.DataFrame(columns=['country', 'count']), 'empty', directory, str)
            self.assertIsNone(result)
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_unknown_only_and_many_countries_render(self):
        frames = [pd.DataFrame({'country': ['Unknown'], 'count': [5]}),
                  pd.DataFrame({'country': ['US', 'DE', 'CN', 'FR', 'GB', 'IN', 'CA', 'JP', 'AU', 'Unknown'],
                                'count': [100, 40, 30, 20, 15, 10, 8, 7, 6, 5]})]
        with tempfile.TemporaryDirectory() as directory:
            for index, frame in enumerate(frames):
                with self.subTest(index=index):
                    result = geography.plot_citation_geography(frame, str(index), directory, str)
                    with Image.open(result) as image:
                        self.assertGreater(image.width, image.height)
                        image.verify()
