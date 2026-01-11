import sys
import unittest
from pathlib import Path

# Add parent directory to path to allow importing modules
sys.path.append(str(Path(__file__).parent.parent))

from utils_system import safe_filename, parse_keywords, short_url, looks_like_url
from utils_image import normalize_text, classify_text

class TestUtilsSystem(unittest.TestCase):
    def test_safe_filename(self):
        """測試檔名特殊字元移除"""
        self.assertEqual(safe_filename("https://google.com"), "google.com")
        self.assertEqual(safe_filename("a/b:c*d?e\"f<g>h|i"), "a_b_c_d_e_f_g_h_i")
        # 測試長度限制 (23 chars)
        long_name = "this_is_a_very_long_filename_that_should_be_truncated"
        self.assertTrue(len(safe_filename(long_name)) <= 23)

    def test_parse_keywords(self):
        """測試關鍵字解析"""
        self.assertEqual(parse_keywords("a,b, c"), ["a", "b", "c"])
        self.assertEqual(parse_keywords("a; b\nc"), ["a", "b", "c"])
        self.assertEqual(parse_keywords(""), [])

    def test_short_url(self):
        """測試網址縮短"""
        url = "http://very-long-url.com/a/b/c/d/e/f"
        self.assertTrue(len(short_url(url, 10)) <= 10)
        self.assertTrue(short_url(url, 10).endswith("..."))
        self.assertEqual(short_url("abc", 10), "abc")

    def test_looks_like_url(self):
        """測試網址格式判斷"""
        self.assertTrue(looks_like_url("http://google.com"))
        self.assertTrue(looks_like_url("https://example.org"))
        self.assertFalse(looks_like_url("not a url"))
        self.assertFalse(looks_like_url("http:// space"))


class TestUtilsImage(unittest.TestCase):
    def test_normalize_text(self):
        """測試文字正規化 (去空白、轉小寫)"""
        self.assertEqual(normalize_text(" Abc  DeF "), "abcdef")
        self.assertEqual(normalize_text("A\nB\tC"), "abc")

    def test_classify_text(self):
        """測試文字分類邏輯"""
        cap = ["captcha"]
        nf = ["not found"]
        bsmi = ["bsmi"]
        login = ["login"]

        # 測試登入
        self.assertEqual(classify_text("Please Login Here", cap, nf, bsmi, login), "登入")
        
        # 測試驗證碼
        self.assertEqual(classify_text("Please enter captcha", cap, nf, bsmi, login), "驗證是否人類")
        
        # 測試商品不存在
        self.assertEqual(classify_text("Product not found error", cap, nf, bsmi, login), "商品不存在")
        
        # 測試 BSMI
        self.assertEqual(classify_text("Product has BSMI mark", cap, nf, bsmi, login), "商品存在 且有BSMI認證")
        
        # 測試無關文字
        self.assertEqual(classify_text("Just some random text", cap, nf, bsmi, login), "無法判斷")


if __name__ == "__main__":
    unittest.main()
