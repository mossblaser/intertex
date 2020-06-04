Intertex example
================

This directory contains three documents:

* `./sphinx_doc_a/ <./sphinx_doc_a/>`_: A sphinx document which references the other two documents.
* `./sphinx_doc_b/ <./sphinx_doc_b/>`_: Another sphinx document.
* `./latex_doc/ <./latex_doc/>`_: An ordinary LaTeX document.

As with intersphinx, intertex requires the referenced documentation is built
first (i.e. ``latex_doc`` and ``sphinx_doc_b`` must be built before
``sphinx_doc_a``). For convenience, a Makefile is provided which will build all
three documents::

    $ make all

The resulting PDFs can be found in:

* `./sphinx_doc_a/build/latex/sphinx_doc_a.pdf <./sphinx_doc_a/build/latex/sphinx_doc_a.pdf>`_
* `./sphinx_doc_b/build/latex/sphinx_doc_b.pdf <./sphinx_doc_b/build/latex/sphinx_doc_b.pdf>`_
* `./latex_doc/latex_doc.pdf <./latex_doc/latex_doc.pdf>`_
