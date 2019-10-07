"""Script for building the documentation in PDF format.

This script is invoked by `make docs-pdf` (Unix systems only!)

It assumes that you have lualatex installed (https://www.tug.org/texlive/).
You must also have the DejaVu fonts installed on your system
(https://dejavu-fonts.github.io).
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).parent


def get_version(filename):
    """Extract the package version"""
    with open(filename, encoding='utf8') as in_fh:
        for line in in_fh:
            if line.startswith('__version__'):
                return line.split('=')[1].strip()[1:-1]
    raise ValueError("Cannot extract version from %s" % filename)


def _patch_line(line):
    if line.startswith('\sphinxhref{') and line.endswith(".svg}}\n"):
        return None
    if line == r'\chapter{References}' + "\n":
        return None
    if line.endswith(r'\label{\detokenize{99_bibliography::doc}}' + "\n"):
        return None
    line = line.replace('{{krotovscheme}.svg}', '{{krotovscheme}.pdf}')
    line = line.replace(
        '{{oct_decision_tree}.svg}', '{{oct_decision_tree}.pdf}'
    )
    if line.startswith(r'\(\newcommand'):
        return None
    if line == r'\begin{split}\begin{equation}' + "\n":
        return None
    if line == r'\end{equation}\end{split}' + "\n":
        return None
    if line == r'\begin{split}\begin{split}' + "\n":
        return r'\begin{split}' + "\n"
    if line == r'\end{split}\end{split}' + "\n":
        return r'\end{split}' + "\n"
    if line == r'  \end{split}\end{split}' + "\n":
        return r'\end{split}' + "\n"
    if line.startswith(r'\release{'):
        version = get_version(ROOT / '../src/krotov/__init__.py')
        line = r'\release{' + version + "}\n"
    if line.startswith(r'\author{'):
        line = r'\author{Michael Goerz \textit{et. al.}}' + "\n"
    return line


def patch_krotov_tex_lines(texfile):
    """Fix errors line-by-line in the given texfile."""
    with tempfile.TemporaryDirectory() as tmpdir:
        orig = Path(tmpdir) / texfile.name
        shutil.copyfile(texfile, orig)
        with orig.open() as in_fh, texfile.open("w") as out_fh:
            for line in in_fh:
                line = _patch_line(line)
                if line is None:
                    continue
                out_fh.write(line)


def patch_krotov_tex(texfile):
    """Fix errors in the given texfile, acting on the whole text."""
    tex = texfile.read_text(encoding='utf8')
    tex = tex.replace(
        r'\begin{equation*}' + "\n" + r'\begin{split}\begin{align}',
        r'\begin{align*}',
    )
    tex = tex.replace(
        r'\end{align}\end{split}' + "\n" + r'\end{equation*}', r'\end{align*}'
    )
    texfile.write_text(tex, encoding='utf8')


def lualatex(texfile):
    """Run lualatex to compile the given texfile."""
    subprocess.run(
        [
            'lualatex',
            '--interaction=nonstopmode',
            '--halt-on-error',
            texfile.name,
        ],
        cwd=texfile.parent,
        check=True,
    )


def main():
    """Main function."""
    texfile = ROOT / '_build/tex/krotov.tex'
    if not texfile.is_file():
        print(f"{texfile} does not exist")
        sys.exit(1)
    patch_krotov_tex_lines(texfile)
    patch_krotov_tex(texfile)
    lualatex(texfile)
    lualatex(texfile)
    sys.exit(0)


if __name__ == "__main__":
    main()
