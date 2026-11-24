# Revised manuscript

The main document is `visionresearch-article.tex`, with the included `scale_diagnostics.tex`, shared bibliography, and three vector figures. `visionresearch-article.pdf` is the compiled review copy (line numbered body). These scientific sources and figures match the Overleaf revision.

Compile from this directory with a TeX distribution supplying `elsarticle` and standard packages:

```bash
tectonic visionresearch-article.tex
```

Alternatively use `latexmk -pdf visionresearch-article.tex`. The class and required packages can be installed from the TeX distribution. Figure regeneration instructions are in the repository README. `REVISION_AUDIT.md` records scientific and implementation checks; the public release tag is `visionresearch-revision-20261124`.

The response letter and received reviewer/author correspondence remain in the author's Overleaf project; they are not part of this public code package.
