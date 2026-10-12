"""The manifest form on /submit/: every field of the schema the form writes has a control and a place for its problems."""

import json
import unittest

from lcsite import submit_form
from lcsite.config import ROOT

SCHEMA = json.loads((ROOT / "schema" / "labconstrictor-app.schema.json").read_text(encoding="utf-8"))


class FormTests(unittest.TestCase):
    """The HTML the script works with."""

    def test_every_field_the_script_writes_is_in_the_schema_and_has_a_control(self) -> None:
        """Each schema field except the fixed ones (schema, platforms) has a named control and an error slot; the form starts hidden."""
        html = submit_form.form_html("../schema/x.json", "https://form.example")
        self.assertIn("data-manifest-form", html)
        self.assertIn(" hidden ", html)
        fields = set(SCHEMA["properties"]) - {"schema", "distribution"} | {"installer", "colab", "pip"}
        for name in fields:
            self.assertIn(f'data-mf-error="{name}"', html, name)
            self.assertTrue(f'name="{name}"' in html or name == "hosts", name)
        self.assertIn('href="https://form.example"', html)
        self.assertNotIn("\n", html)


if __name__ == "__main__":
    unittest.main()
