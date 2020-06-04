"""
A plugin for the Sphinx documentation generator: like Intersphinx for
Sphinx-built PDF documentation.

See README for usage instructions.
"""

from sphinxcontrib.intertex.version import __version__

import os

import re

import glob
import importlib
import inspect

from docutils import nodes
from sphinx.util.nodes import make_refnode

from sphinx.util.texescape import tex_replace_map

from sphinx.util import logging


logger = logging.getLogger(__name__)


BRACKETED_MODULE_NAME_REGEX = re.compile(r"\{([a-zA-Z0-9_\.]+)\}")
"""
A regular expression matching Python module names within curly brackets, e.g.
``{sphinxcontrib.intertex}``. Contains a capture group for the module name
itself, e.g. ``sphinxcontrib.intertex``.
"""


AUX_ENTRY_REGEX = re.compile(r"\\newlabel(.*)")
r"""
Regular expression matching a \newlabel macros within a LaTeX ``*.aux`` file.
Contains a capture group for the arguments of the macro.
"""


BRACKETED_VALUE_REGEX = re.compile(r"\{([^\{\}]*)\}")
"""
Regular expression matching a string of the form ``{someting in here}``, e.g. a
macro argument. Contains a capture group with the contained text.
"""


def expand_aux_file_names(app, config):
    """
    Sphinx ``config-inited`` event handler. Expands module names and glob
    patterns in filenames in the ``intertex_mapping`` config dictionary.

    Performs the following substitutions:

    * Replaces ``{module.name.here}`` with the directory that module resides
      in.
    * Expands :py:mod:`glob` patterns (e.g. ``*``).

    If a provided path does not point to a file, a log message is printed and
    that entry in ``intertex_mapping`` is dropped.

    If a provided path expands to multiple filenames, the first is used and a
    log message is printed.
    """
    new_intertex_mapping = {}
    for bibentry, filename_pattern in config.intertex_mapping.items():
        # Substitute {python.module.name} for the path to that module's
        # directory
        try:
            filename_pattern = BRACKETED_MODULE_NAME_REGEX.sub(
                lambda match: os.path.dirname(
                    inspect.getsourcefile(importlib.import_module(match.groups()[0]))
                )
                + "/",
                filename_pattern,
            )
        except ImportError as e:
            logger.error(
                "Intertex couldn't import module %s (%s), skipping %r",
                e.name,
                e.msg,
                bibentry,
            )
            continue

        filename_pattern = os.path.normpath(filename_pattern)

        # Expand glob operators
        filenames = glob.glob(filename_pattern)
        if len(filenames) == 0:
            logger.error(
                "Intertex couldn't find any aux files matching %s, skipping %r",
                filename_pattern,
                bibentry,
            )
            continue

        if len(filenames) > 1:
            logger.error(
                "Intertex found multiple aux files matching %s for %r, will use only %s",
                filename_pattern,
                bibentry,
                filenames[0],
            )

        new_intertex_mapping[bibentry] = filenames[0]

    config.intertex_mapping = new_intertex_mapping


def read_mapping(app):
    """
    Sphinx ``config-inited`` event handler. Reads all ``*.aux`` files defined
    in ``intertex_mapping`` and extracts the section and page number of each
    label defined within.

    Populates ``env.intertex_refs`` with a dictionary of the form ``{label:
    (bibentry, section, page), ...}``. Here ``label`` is a Sphinx label,
    ``bibentry`` is the bibliography entry to point to and ``section`` and
    ``page`` give the section and page numbers within the PDF documentation.

    Where a label is defined multiple times (perhaps by multiple documents), a
    warning is produced and one target will be picked arbitrarily.
    """
    env = app.builder.env
    env.intertex_refs = {}

    citation_domain = env.get_domain("citation")
    citation_refs = citation_domain.citation_refs

    already_warned_about_redefinition = set()

    for bibentry, aux_filename in app.config.intertex_mapping.items():
        # Mark citation as used (to suppress unused citation warnings).
        # Ideally, we would do this only if a reference is later used.
        # Unfortunately, the ``missing-reference`` event is fired after the
        # citations domain performs its test for unused citations so this would
        # be too late.
        docnames = citation_refs.setdefault(bibentry, set())
        docnames.add("")

        with open(aux_filename, "r") as f:
            for line in f:
                match = AUX_ENTRY_REGEX.match(line)
                if match:
                    args = BRACKETED_VALUE_REGEX.findall(match.groups()[0])
                    label = args[0]
                    section = args[1]
                    page = args[2]

                    # Allow targeting both the full label (when pointing at
                    # normal LaTeX documents) and after-the-colon part of the
                    # label which sphinx places the value label in.
                    sphinx_targets = [label]
                    if ":" in label:
                        sphinx_targets.append(label.partition(":")[2])
                    
                    for sphinx_target in sphinx_targets:
                        if (
                            sphinx_target in env.intertex_refs
                            and sphinx_target not in already_warned_about_redefinition
                        ):
                            logger.warning(
                                "Intertex sphinx reference %s defined multiple times",
                                sphinx_target,
                            )
                            already_warned_about_redefinition.add(sphinx_target)

                        env.intertex_refs[sphinx_target] = (bibentry, section, page)


def get_citation_ref(env, bibentry):
    """
    Given the name of a citation (i.e. the name you'd use in ``[here]_``),
    return the (docname, labelid) pair which references the citation
    definition.

    If no citation definition exists for the provided label, returns ("", "").
    """
    # XXX: This uses an undocumented/private (not sure which...) part of the
    # citations domain's API.
    citations = env.get_domain("citation").citations
    docname, labelid, lineno = citations.get(bibentry, ("", "", 0))
    return (docname, labelid)


def make_bib_reference(app, bibentry, refdoc):
    """
    Create a docutils node with a reference to to an entry in the bibliography.

    If the bibliography entry exists, the returned node will be rendered as a
    hyperlink of the form ``[my-bibentry-label]`` pointing to the entry in the
    bibliography. Otherwise, a non-hyperlinked entry will be returned and a
    warning printed.
    """
    docname, labelid = get_citation_ref(app.builder.env, bibentry)

    if docname:
        if app.builder.format == "latex":
            # Bodge: To make the LaTeX writer produce a citation in the
            # output, we must create a citation_reference node. If we
            # created a ref node (as we do for other output modes), two
            # problems would arise:
            #
            # * The LaTeX output doesn't include labels for
            #   bibliography entries so the ref would not produce a
            #   valid hyperlink
            # * When latex_show_pagerefs is used, the ref would result
            #   in the page number of the bibliography being shown
            #   which would be confusing. (Especially as the ref
            #   would not resolve and so ?? would be shown).
            #
            # Ordinarily, citation_reference nodes would have been
            # converted into pending_xrefs long ago by
            # sphinx.domains.citation.CitationReferenceTransform,
            # however when using the LaTeX builder, another
            # transformer,
            # sphinx.builders.latex.transforms.CitationReferenceTransform,
            # immediately undoes this transformation causing them to
            # survive all the way to the writer output.
            bibref = nodes.citation_reference(text="[{}]".format(bibentry))
            bibref["docname"] = docname
            bibref["refname"] = labelid
            return bibref
        else:
            # Construct a reference to the citation definition.
            #
            # Note that we can't just make a citation_reference because
            # these have already been transformed into pending_xrefs by
            # sphinx.domains.citation.CitationReferenceTransform in an
            # earlier build step (which in turn are being resolved
            # right now).
            return make_refnode(
                app.builder,
                refdoc,
                docname,
                labelid,
                nodes.Text("[{}]".format(bibentry)),
            )
    else:
        logger.warning("Intertex found no citation for %r", bibentry)
        return nodes.Text("[{}]".format(bibentry))


def make_pdf_reference(app, bibentry, section, page, contnode, refdoc):
    """
    Create a reference to a location in a PDF formatted according to
    the ``intertex_reference_format``.

    The ``intertex_reference_format`` config option must be a string containing
    the following which will be substituted as specified.

    ``{label}``
        The text which is being cross-referenced (i.e. contnode).
    
    ``{bibref}``
        The bibliographic reference.
    
    ``{page}``
        The page number in the referenced PDF.
    
    ``{section}``
        The section number in the referenced PDF.

    Parameters
    ==========
    app
        Sphinx application.
    bibentry : str
        Name of bibliography entry to cite.
    section : str
        Name of the section in the PDF being cited.
    page : str
        Page number in the PDF being cited.
    contnode : node
        Docutils node containing the label being cited.
    refdoc : str
        Document name of document this reference will be inserted into.
    """
    bibref = make_bib_reference(app, bibentry, refdoc)

    format_parts = iter(
        BRACKETED_VALUE_REGEX.split(app.config.intertex_reference_format)
    )
    new_contnode = nodes.inline()
    try:
        while True:
            new_contnode += nodes.Text(next(format_parts))
            new_contnode += {
                "label": contnode,
                "bibref": bibref,
                "section": nodes.Text(section),
                "page": nodes.Text(page),
            }[next(format_parts)]
    except StopIteration:
        pass

    return new_contnode


def missing_reference(app, env, node, contnode):
    """
    Sphinx ``missing-reference`` event handler. Attempts to find missing
    references in any of the documents listed in ``intertex_mapping`` and
    substitute a suitable reference.
    """
    if app.builder.format in app.config.intertex_formats:
        reftargets_to_try = [node["reftarget"]]

        # Bodge: Sphinx prepends "module-" to module reference labels...
        if node["reftype"] == "mod":
            reftargets_to_try.append("module-{}".format(node["reftarget"]))

        # Bodge: Labels are normalised in LaTeX output. The following relies on
        # internals of the LaTeX writer...
        for reftarget in list(reftargets_to_try):
            reftargets_to_try.append(
                reftarget
                    .translate(tex_replace_map)
                    .encode("ascii", "backslashreplace")
                    .decode("ascii")
                    .replace("\\", "_")
            )
        
        # Bodge: Sometimes underscores get converted to dashes...
        for reftarget in list(reftargets_to_try):
            reftargets_to_try.append(reftarget.replace("_", "-"))

        for reftarget in reftargets_to_try:
            if reftarget in env.intertex_refs:
                bibentry, section, page = env.intertex_refs[reftarget]
                return make_pdf_reference(app, bibentry, section, page, contnode, node["refdoc"])


def setup(app):
    # A dictionary giving the locations of *.aux files generated by LaTeX
    # builds of Sphinx documentation.
    #
    #     {"bib-entry-label": "/path/to/doc.aux", ...}
    #
    # See expand_aux_file_names for substitutions applied to path names.
    app.add_config_value("intertex_mapping", {}, True)
    
    # Format for references inserted into the documentation. See
    # make_pdf_reference.
    app.add_config_value(
        "intertex_reference_format", "{label} ({bibref}, page {page})", True
    )
    
    # The Sphinx output formats for which intertex is enabled.
    app.add_config_value("intertex_formats", ["latex"], True)
    
    app.connect("config-inited", expand_aux_file_names)
    app.connect("builder-inited", read_mapping)

    # NB: priority=450 gives this extension priority over Intersphinx (which
    # has priority=500). This means that for LaTeX/PDF documentation, Intertex
    # references will be preferred.
    app.connect("missing-reference", missing_reference, priority=450)

    return {
        "version": __version__,
        "parallel_read_safe": True,
    }
