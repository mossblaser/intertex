Welcome to sphinx_doc_a's documentation!
========================================

This documentation includes references both to some :ref:`local objects
<sphinx_doc_a_definitions>` and some in :ref:`another document
<sphinx_doc_b_definitions>`. It even refers to some parts of an ordinary
:ref:`LaTeX document <latex-doc-intro>`!

See :py:class:`AnInternalClass` for a locally defined object and
:py:class:`SomeExternalClass` for one defined in another document (via
intertex). Also see :py:class:`str` for one found by Intersphinx.

.. [sphinx-doc-b] The PDF in ``examples/sphinx_doc_b/build/latex/sphinx_doc_b.pdf``.

.. [latex-doc] The PDF in ``examples/latex_doc/latex_doc.pdf``.


.. _sphinx_doc_a_definitions:

Definitions
-----------

Here are some definitions defined locally in this document.

.. py:class:: AnInternalClass

    A class defined in sphinx_doc_a. A subclass of
    :py:class:`SomeExternalClass`.
    
    .. py:method:: bar()
    
        Overrides :py:meth:`SomeExternalClass.bar`.

