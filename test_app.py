import unittest
from app import app, safe_to_bytearray, WORDLISTS

class TestBIP39DotmapApp(unittest.TestCase):

    def setUp(self):
        # Configure Flask app for testing
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_wordlist_loading(self):
        # Ensure standard wordlists are loaded (especially English)
        self.assertIn('english', WORDLISTS)
        self.assertEqual(len(WORDLISTS['english']), 2048)
        self.assertEqual(WORDLISTS['english'][0], 'abandon')
        self.assertEqual(WORDLISTS['english'][2047], 'zoo')

    def test_safe_to_bytearray_normal(self):
        # Basic conversion
        test_str = "hello world"
        result = safe_to_bytearray(test_str)
        self.assertIsInstance(result, bytearray)
        self.assertEqual(result, bytearray(b"hello world"))

    def test_safe_to_bytearray_with_null_bytes(self):
        # Null bytes must be stripped
        test_str = "hello\x00world"
        result = safe_to_bytearray(test_str)
        self.assertEqual(result, bytearray(b"helloworld"))

    def test_safe_to_bytearray_overflow_prevention(self):
        # String exceeding max length limit should be sliced
        test_str = "a" * 15000
        result = safe_to_bytearray(test_str)
        self.assertEqual(len(result), 10000)

    def test_get_index_page(self):
        # Test default GET request loads successfully
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn("BIP39 Mnemonic Dotmap", response.data.decode('utf-8'))

    def test_post_valid_12_words(self):
        # 12 valid words in English
        phrase = "abandon ability able about above absent absorb abstract absurd abuse access accident"
        response = self.client.post('/', data={
            'language': 'english',
            'words': phrase
        })
        self.assertEqual(response.status_code, 200)
        data_str = response.data.decode('utf-8')
        # Results table should be rendered
        self.assertIn("Visualization & Dot Map Table", data_str)
        self.assertIn("abandon", data_str)
        self.assertIn("accident", data_str)
        # Verify 1-based index mapping is shown (e.g. abandon is index 1, ability is index 2, accident is index 12)
        self.assertIn("1</span>", data_str)
        self.assertIn("2</span>", data_str)
        self.assertIn("12</span>", data_str)
        # Check binary/dot representation
        self.assertIn("○", data_str)
        self.assertIn("●", data_str)

    def test_post_valid_24_words(self):
        # 24 valid words in English
        phrase = "abandon " * 24
        response = self.client.post('/', data={
            'language': 'english',
            'words': phrase
        })
        self.assertEqual(response.status_code, 200)
        data_str = response.data.decode('utf-8')
        self.assertIn("abandon", data_str)
        # Word count is exactly 24
        self.assertIn("24", data_str)

    def test_post_invalid_word_count(self):
        # Under 12 words (e.g. 5 words)
        phrase = "abandon ability able about above"
        response = self.client.post('/', data={
            'language': 'english',
            'words': phrase
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("Please enter from 12 to 24 words", response.data.decode('utf-8'))

        # Over 24 words (e.g. 25 words)
        phrase = "abandon " * 25
        response = self.client.post('/', data={
            'language': 'english',
            'words': phrase
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("Please enter from 12 to 24 words", response.data.decode('utf-8'))

    def test_post_unmatched_words(self):
        # 12 words where some don't exist in the English BIP39 list
        phrase = "abandon ability able about above absent absorb abstract absurd abuse access NOTAWORD"
        response = self.client.post('/', data={
            'language': 'english',
            'words': phrase
        })
        self.assertEqual(response.status_code, 200)
        data_str = response.data.decode('utf-8')
        # Warning about unmatched words should exist
        self.assertIn("Warning: The following word(s) did not match", data_str)
        self.assertIn("NOTAWORD", data_str)
        self.assertIn("NOT FOUND", data_str)

if __name__ == '__main__':
    unittest.main()
