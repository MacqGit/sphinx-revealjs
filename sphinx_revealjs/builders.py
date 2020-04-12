"""Definition for sphinx custom builder."""
from typing import Dict, List, Tuple

from sphinx.builders.html import StandaloneHTMLBuilder

from sphinx_revealjs.directives import raw_json
from sphinx_revealjs.writers import RevealjsSlideTranslator


def static_resource_uri(src: str, prefix: str = None) -> str:
    """Build static path of resource."""
    local_prefix = "_static" if prefix is None else prefix
    if src.startswith("http://") or src.startswith("https://"):
        return src
    return f"{local_prefix}/{src}"


class RevealjsContext(object):
    """Context object for Reveal.js script region."""

    def __init__(self, script_files: List[str]):  # noqa
        self.script_files = script_files


class RevealjsHTMLBuilder(StandaloneHTMLBuilder):
    """Sphinx builder class to generate Reveal.js presentation HTML.

    This manage theme path and configure default options.
    """

    name = "revealjs"
    default_translator_class = RevealjsSlideTranslator

    def __init__(self, app):  # noqa: D107
        super().__init__(app)
        self.revealjs_slide = None
        self.css_files = [
            "_static/revealjs/css/reveal.css",
            "_static/revealjs/lib/css/zenburn.css",
        ]

    def init(self):  # noqa
        super().init()
        self.revealjs_script_files = [
            static_resource_uri(src)
            for src in getattr(self.config, "revealjs_script_files", [])
        ]
        self.revealjs_context = RevealjsContext(self.revealjs_script_files)

    def get_theme_config(self) -> Tuple[str, Dict]:
        """Find and return configuration about theme (name and option params).

        Find theme and merge options.
        """
        theme_name = getattr(self.config, "revealjs_theme", "sphinx_revealjs")
        theme_options = getattr(self.config, "revealjs_theme_options", {})
        config = raw_json(theme_options.get("revealjs_config", ""))
        theme_options["revealjs_config"] = config
        return theme_name, theme_options

    def get_doc_context(self, docname, body, metatags):
        """Return customized context.

        if source has ``revealjs_slide`` property, add configures.
        """
        ctx = super().get_doc_context(docname, body, metatags)
        if self.revealjs_slide:
            ctx["revealjs_slide"] = self.revealjs_slide.attributes
            ctx["revealjs_config"] = self.revealjs_slide.content
        ctx["revealjs"] = self.revealjs_context
        return ctx
