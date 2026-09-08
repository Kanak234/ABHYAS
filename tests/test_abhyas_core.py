import unittest
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

class TestAbhyasCore(unittest.TestCase):
    def test_lesson_structure(self):
        paath_dir = os.path.join(ROOT, 'paath')
        self.assertTrue(os.path.isdir(paath_dir), "paath directory must exist")
        lessons = [f for f in os.listdir(paath_dir) if not f.startswith('.')]
        self.assertGreater(len(lessons), 0, "At least one lesson module must be present")

    def test_padho_file_presence(self):
        padho = os.path.join(ROOT, 'PADHO.txt')
        self.assertTrue(os.path.isfile(padho), "PADHO.txt Hindi documentation must exist")

    def test_tools_integrity(self):
        tools_dir = os.path.join(ROOT, 'tools')
        self.assertTrue(os.path.isdir(tools_dir), "tools directory must exist")

if __name__ == '__main__':
    unittest.main()
