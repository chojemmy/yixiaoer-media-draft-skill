"""Offline behavior tests. No upload, draft save, or credentials required."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


class MediaTests(unittest.TestCase):
    def run_script(self, name, *args):
        return subprocess.run([sys.executable, str(ROOT / "scripts" / name), *map(str, args)],
                              capture_output=True, encoding="utf-8")

    def test_embedded_final_wins_and_project_prefix_is_exact(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            article = root / "002_20260906_模型.md"
            article.write_text('![[002_final.mp4]]', encoding='utf-8')
            for folder, files in [('002_项目', ['002_final.mp4', '002_exp_final.mp4']),
                                  ('0020_其他项目', ['002_final.mp4'])]:
                target = root / 'media' / folder
                target.mkdir(parents=True)
                for file in files:
                    (target / file).touch()
            result = self.run_script('locate_media.py', '--article', article, '--media-root', root / 'media')
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(len(data['candidates']), 1)
            self.assertIn('002_项目', data['selected']['folder'])

    def test_ambiguous_and_empty_results_are_not_auto_selected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            article = root / '003_项目.md'
            article.write_text('脚本', encoding='utf-8')
            media = root / 'media' / '003_项目'
            media.mkdir(parents=True)
            for n in ['a_final.mp4', 'b_exp_final.mp4']:
                (media / n).touch()
            result = self.run_script('locate_media.py', '--article', article, '--media-root', media.parent)
            data = json.loads(result.stdout)
            self.assertTrue(data['needs_user_choice'])
            self.assertIsNone(data['selected'])
            other = root / '004_空项目.md'
            other.touch()
            data = json.loads(self.run_script('locate_media.py', '--article', other, '--media-root', media.parent).stdout)
            self.assertTrue(data['not_found'])
            self.assertIsNone(data['selected'])

    def test_missing_article_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            result = self.run_script('locate_media.py', '--article', Path(temp) / 'missing.md', '--media-root', temp)
            self.assertNotEqual(result.returncode, 0)

    def test_cover_dimensions_size_and_opaque_panel(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            frame = root / 'frame.jpg'
            Image.new('RGB', (1920, 1080), (200, 90, 10)).save(frame)
            vertical, horizontal = root / '竖.jpg', root / '横.jpg'
            result = self.run_script('make_cover.py', '--input', frame, '--vertical-output', vertical,
                                     '--horizontal-output', horizontal, '--title', '大模型还是小模型',
                                     '--subtitle', '探索用大，执行用小', '--eyebrow', '企业AI',
                                     '--vertical-crop-bottom', 190)
            self.assertEqual(result.returncode, 0, result.stderr)
            for path, size in [(vertical, (1080, 1440)), (horizontal, (1920, 1080))]:
                with Image.open(path) as im:
                    self.assertEqual(im.size, size)
                    # Clean bottom corner is opaque navy, not the orange source frame.
                    self.assertLess(max(im.getpixel((size[0] - 10, size[1] - 10))), 60)
                self.assertLessEqual(path.stat().st_size, 500000)
            invalid = self.run_script('make_cover.py', '--input', frame, '--vertical-output', vertical,
                                      '--horizontal-output', horizontal, '--title', '模型',
                                      '--vertical-crop-bottom', 1080)
            self.assertNotEqual(invalid.returncode, 0)


if __name__ == '__main__':
    unittest.main()
