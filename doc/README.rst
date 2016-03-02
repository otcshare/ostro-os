This doc directory contains technical and process information about the Ostro (TM) OS.

Putting the documentation within the source project gives us a straightforward way to keep
the project documentation and source code in sync.
This also makes it easier for developers to collaborate by
using a single source for document files, using git as a document repository, and
using GitHub's moderation and approval process.  Documentation changes go through
the same approval processes as the code.

While there may be documents in progress within this ``doc/`` folder, only files actually
referenced by the index.rst file (or .rst files referenced by those referenced files)
get included in the public website documentation.

Folder structure
================

top-level doc directory
    index.rst "main page"

howtos_
    Articles explaining how to do certain tasks covering
    development on (or for) Ostro OS as well as using and contributing to it.

architecture_
    Technical Architecture information about the Ostro OS and its components

quick_start_
    Getting Started Guide and associated subtopics for setting up Ostro OS development

sphinx_build
    Sphinx_ configuration and build files for the Ostro Project's website.  When processed,
    HTML output is contained within this folder in the ``_build/html`` folder. We use
    two different themes: one simple theme for generating an HTML site that can be
    viewed locally (this is the theme included with the source code), and a second
    more complex theme that's used to generate the public facing website accessed
    via the internet.  This latter theme is matched to the theme used on the main
    ostroproject.org website and maintained by the website team.

Generate the HTML documentation
===============================

To generate the HTML version of the documentation, you need to install Sphinx_ on your system.

* On Linux-based system: install the ``python-sphinx`` package
* On Windows-based system: follow the instructions on the Sphinx_ website

Once the tool has been installed, from the ``sphinx_build`` folder, run::

    make html

You can now view the entire documentation set for that version by pointing your favorite
browser at :file:`doc/sphinx_build/_build/html/index.html`

.. _Sphinx: http://www.sphinx-doc.org/
.. _howtos: howtos
.. _architecture: architecture
.. _quick_start: quick_start

