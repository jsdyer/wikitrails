import json
from pathlib import Path
import re
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from search_metadata import add_search_metadata


class SearchMetadataTests(unittest.TestCase):
    def test_safe_json_and_single_canonical_for_initialized_tool(self):
        tool = {"id": "example", "title": "A </script><script>bad()", "description": "Read & compare",
                "source": "https://github.com/jsdyer/example", "url": "/example/"}
        page = add_search_metadata('<head><title>Read &amp; compare · CoolCode</title><link rel="canonical" href="https://coolcode.ca/example/"></head>', tool)
        self.assertNotIn("</script><script>", page)
        data = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', page).group(1))
        app = data["@graph"][0]
        self.assertEqual(app["name"], tool["title"])
        self.assertEqual(app["url"], "https://coolcode.ca/example/")
        self.assertEqual(page.count('rel="canonical"'), 1)
        self.assertEqual(app["offers"]["price"], "0")
        self.assertNotIn("aggregateRating", app)

    def test_fork_does_not_claim_the_coolcode_domain(self):
        tool = {"id": "example", "title": "Example", "description": "Read", "url": "/example/",
                "source": "https://github.com/another-owner/example"}
        page = add_search_metadata('<head><title>Read · Example</title></head>', tool)
        self.assertNotIn("coolcode.ca", page)
