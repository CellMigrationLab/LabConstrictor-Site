"""Guides kept in other repositories: link and picture conversion for the site (lcsite.sources)."""

import unittest

from lcsite import sources


class SourceLinkTests(unittest.TestCase):
    """How a fetched page's links and pictures become site pages or absolute addresses."""

    def test_relative_link_or_picture_stops_the_build(self) -> None:
        """A relative link or picture would break on the site, so it fails and names the guide."""
        with self.assertRaises(SystemExit) as ctx:
            sources.check_links("See [x](other.md) and ![p](shot.png)", "repo/docs/user-guide.md")
        self.assertIn("repo/docs/user-guide.md", str(ctx.exception))
        sources.check_links("[ok](https://example.org/a) [here](#top)", "x")

    def test_link_to_an_imported_guide_points_at_the_site_page(self) -> None:
        """A link to another imported guide's file on GitHub becomes a site link; other links stay."""
        pages = {("o/r", "docs/user-guide.md"): "r"}
        text = "[a](https://github.com/o/r/blob/main/docs/user-guide.md#x) [b](https://github.com/o/r/blob/main/README.md)"
        out = sources.site_links(text, pages)
        self.assertIn("[a](../r/index.md#x)", out)
        self.assertIn("[b](https://github.com/o/r/blob/main/README.md)", out)

    def test_relative_links_and_pictures_are_resolved_in_their_repository(self) -> None:
        """A page written for its repository's own docs: a relative link becomes the file on GitHub (then the site page when imported),
        a picture its raw address; anchors and absolute links stay; the result passes check_links."""
        text = "[p](PROTOCOL.md#rules) [up](../README.md) ![s](img/a.png) [abs](https://x.org/a.md) [here](#top)"
        out = sources.resolve_relative(text, "O/r", "docs/MANIFEST.md")
        self.assertIn("[p](https://github.com/O/r/blob/main/docs/PROTOCOL.md#rules)", out)
        self.assertIn("[up](https://github.com/O/r/blob/main/README.md)", out)
        self.assertIn("![s](https://raw.githubusercontent.com/O/r/main/docs/img/a.png)", out)
        self.assertIn("[abs](https://x.org/a.md) [here](#top)", out)
        sources.check_links(out, "O/r/docs/MANIFEST.md")
        self.assertIn("[p](../protocol/index.md#rules)", sources.site_links(out, {("O/r", "docs/PROTOCOL.md"): "protocol"}))

    def test_a_relative_link_out_of_the_repository_stops_the_build(self) -> None:
        """A link that climbs above the repository cannot be resolved: the build stops and names the page."""
        with self.assertRaises(SystemExit) as ctx:
            sources.resolve_relative("[x](../../elsewhere.md)", "O/r", "docs/MANIFEST.md")
        self.assertIn("O/r/docs/MANIFEST.md", str(ctx.exception))

    def test_a_docs_site_address_becomes_the_page_file(self) -> None:
        """https://<owner>.github.io/<repo>/<PAGE>/ of the same owner becomes docs/<PAGE>.md (spelled as the guide list spells the owner),
        so an imported page links here; this site's own addresses and other owners' sites stay as they are."""
        text = ("[m](https://cellmigrationlab.github.io/LabConstrictor-Tools/MANIFEST/#hosts) "
                "[s](https://cellmigrationlab.github.io/LabConstrictor-Site/guides/) [o](https://other.github.io/Repo/PAGE/)")
        out = sources.docs_site_to_files(text, "CellMigrationLab")
        self.assertIn("[m](https://github.com/CellMigrationLab/LabConstrictor-Tools/blob/main/docs/MANIFEST.md#hosts)", out)
        self.assertIn("[s](https://cellmigrationlab.github.io/LabConstrictor-Site/guides/)", out)
        self.assertIn("[o](https://other.github.io/Repo/PAGE/)", out)



if __name__ == "__main__":
    unittest.main()
