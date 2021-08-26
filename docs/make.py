# Originally from https://github.com/mitmproxy/pdoc/tree/main/docs/make.py
# Modified for use with TouchPortalAPI
# Released back into the public domain.

import pdoc
import shutil
from pathlib import Path

# from pygments.formatters.html import HtmlFormatter
# from pygments.lexers.python import PythonLexer
# from markupsafe import Markup

here = Path(__file__).parent
mod_name = "TouchPortalAPI"
docs_dir = here  # / "docs"
src_dir = here / ".." / mod_name
repo_url = "https://github.com/KillerBOSS2019/TouchPortal-API/"
home_url = "https://KillerBOSS2019.github.io/TouchPortal-API/"

# Get current TouchPortalAPI version
from sys import path as sys_path
sys_path.insert(1, src_dir)
from TouchPortalAPI import (__version__ as api_version)
# from re import search
# api_version = search(
#   r'__version__ = "(.+?)"', (src_dir / "__init__.py").read_text("utf8")
# ).group(1)

if __name__ == "__main__":
    env = pdoc.render.env
    env.globals["package_name"] = mod_name
    env.globals["package_version"] = api_version

    # Format/publish plugin example?
    # example = here / ".." / "examples" / "plugin_example.py"
    # env.globals["example_html"] = Markup(pygments.highlight(example.read_text("utf8"), PythonLexer(), HtmlFormatter(style="friendly")))

    # clean up old docs
    try:
        if docs_dir != here:
            if docs_dir.is_dir():
                shutil.rmtree(docs_dir)
        else:
            for f in docs_dir.rglob("*.html"):
                f.unlink()
    except OSError as e:
        print(f"Error trying to remove old docs: {e.strerror}")

    # Render main docs
    pdoc.render.configure(
        template_directory = here,
        docformat = "google",
        footer_text = f"{mod_name} v{api_version}",
        edit_url_map={
            mod_name: f"{repo_url}blob/main/{mod_name}/",
            # example: f"{repo_url}blob/main/examples/",
        },
        # logo="/logo.svg",
        # logo_link = home_url,
    )
    pdoc.pdoc(
        mod_name,
        # example,
        output_directory = docs_dir,
    )
