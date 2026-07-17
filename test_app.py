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

    def test_post_xor_encryption(self):
        # Test XOR Masking Advanced Encryption Method
        phrase = "abandon ability able about above absent absorb abstract absurd abuse access accident"
        response = self.client.post('/', data={
            'language': 'english',
            'words': phrase,
            'encryption_method': 'xor'
        })
        self.assertEqual(response.status_code, 200)
        data_str = response.data.decode('utf-8')
        # Decryption Key guide must be visible
        self.assertIn("Manual Decryption Keys & Guide", data_str)
        self.assertIn("XOR Masking active", data_str)
        self.assertIn("Decryption Key (Vernam)", data_str)
        # Verify unencrypted dotmap collapsible area is present
        self.assertIn("Verify Normal (Unencrypted) Dot Map", data_str)

    def test_post_permutation_encryption(self):
        # Test Bit Permutation Advanced Encryption Method
        phrase = "abandon ability able about above absent absorb abstract absurd abuse access accident"
        response = self.client.post('/', data={
            'language': 'english',
            'words': phrase,
            'encryption_method': 'permutation'
        })
        self.assertEqual(response.status_code, 200)
        data_str = response.data.decode('utf-8')
        # Decryption Key guide must be visible
        self.assertIn("Manual Decryption Keys & Guide", data_str)
        self.assertIn("Bit Permutation active", data_str)
        self.assertIn("COLUMN RE-ORDERING REFERENCE CARD", data_str)
        # Verify unencrypted dotmap collapsible area is present
        self.assertIn("Verify Normal (Unencrypted) Dot Map", data_str)

    def test_permutation_ltr_mapping_calculation(self):
        # Explicitly test left-to-right mapping calculation logic
        # perm corresponds to list(range(12)) but reversed
        perm = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
        decryption_mapping = []
        for k in range(1, 13):
            orig_idx = k - 1
            j = perm.index(orig_idx)
            encrypted_pos = j + 1
            decryption_mapping.append({
                'original_pos': k,
                'encrypted_pos': encrypted_pos
            })

        # Original position 1 (orig_idx 0) should find j = 11 -> encrypted_pos = 12
        self.assertEqual(decryption_mapping[0]['original_pos'], 1)
        self.assertEqual(decryption_mapping[0]['encrypted_pos'], 12)
        # Original position 2 (orig_idx 1) should find j = 10 -> encrypted_pos = 11
        self.assertEqual(decryption_mapping[1]['original_pos'], 2)
        self.assertEqual(decryption_mapping[1]['encrypted_pos'], 11)
        # Original position 12 (orig_idx 11) should find j = 0 -> encrypted_pos = 1
        self.assertEqual(decryption_mapping[11]['original_pos'], 12)
        self.assertEqual(decryption_mapping[11]['encrypted_pos'], 1)

if __name__ == '__main__':
    unittest.main()
