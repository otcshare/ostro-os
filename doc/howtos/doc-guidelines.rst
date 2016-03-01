.. _doc_guidelines:

Documentation Guidelines for the Ostro |trade| Project
######################################################

Ostro Project content is written using the `reStructuredText`_ markup language (.rst file extension)
with sphinx extensions, and processed using sphinx to create a formatted
standalone website.  Developers can view this content either in its raw form
as .rst markup files, or (with sphinx installed) they can run the makefile (or make.bat on windows) to generate
the HTML content and view it with a web browser directly
from their workstation's drive.
This same .rst content is also fed into the Ostro Project's public website documentation
area (with a different theme applied).

You can read details about `reStructuredText`_
and about `Sphinx extensions`_ from their respective websites.

.. _Sphinx extensions: http://www.sphinx-doc.org/en/stable/contents.html
.. _reStructuredText: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html
.. _Sphinx Inline Markup:  http://sphinx-doc.org/markup/inline.html#inline-markup

Folder structure
================

top-level doc directory
    index.rst "main page"

howtos
    Articles explaining how to do certain tasks covering
    development on (or for) Ostro OS as well as using and contributing to it.

architecture
    Technical Architecture information about the Ostro OS and its components

quick_start
    Getting Started Guide and associated subtopics for setting up Ostro OS development

sphinx_build
    Sphinx configuration and build files for the Ostro Project's website.  When processed, 
    HTML output is contained within this folder in the _build/html folder.



Headings
========

For consistency, please use just an underline indicator for headings (not both over- and under lines).

* For the document title (h1) use "#" for the underline character
* for the first section heading level (h2) use "="
* for the second section heading level (h3) use "-"
* and for the third section heading level (h4) use "^"

Remember that the underline must be at least as long as the title it's under.


Markup samples
==============

Some common reST inline markup samples:

* one asterisk: ``*text*`` for emphasis (*italics*),
* two asterisks: ``**text**`` for strong emphasis (**boldface**), and
* backquotes: ````text```` for inline code samples.

List markup is natural: just place an asterisk at
the start of a paragraph and indent properly for continuation lines.  For numbered lists
start with a 1. or a. for example, and continue with autonumbered bu using a ``#`` sign::

   * This is a bulleted list.
   * It has two items, the second
     item uses two lines.

   1. This is a numbered list.
   2. It has two items too.

   a. This is a numbered list using alphabetic list headings
   #. It has three items (and uses autonumbering for the rest of the list)
   #. Here's the third item


If asterisks or backquotes appear in running text and could be confused with
inline markup delimiters, they must be escaped with a backslash ("\\")

Sphinx Inline Markup
====================

Sphinx supports a large number of inline markup elements used to tag text with special
meanings and output formatting. (You can refer to the `Sphinx Inline Markup`_
documentation for the full list).   Here are some of the more useful markup notations
for our use:

* Use the 'command' markup when the name of a specific command is
  used as part of a paragraph for emphasis. Use the ``.. code-block::``
  directive to supply full actionable commands as part as a series of
  steps.

   :command:`make`

   ``:command:`command```

* Use the 'file' markup to emphasize a filename or directory. Do not
  use the markup inside a code-block but use it inside all notices that
  contain files or directories.

   :file:`collaboration.rst` :file:`doc/collaboration/figures`

   ``:file:`filename.ext` :file:`path/or/directory```

  You can also use the \`\`inline code\`\` markup (double backticks) to indicate filenames.


.. _internal-linking:

Internal Cross-Reference Linking
================================

Normal ReST linking is only supported within the current file. With Sphinx however, we can create 
and link to references anywhere within the Ostro Project documentation.   
Each file should have a reference label before its title so it may
be referenced from another file. These reference labels must be unique.   For example the top
of this .rst file is:


.. code-block:: rst

   .. _doc_guidelines:

   Documentation Guidelines for the Ostro |trade| Project
   ######################################################


Other .rst documents can link to this document using the ``:ref:`doc_guidelines``` tag and
it will show up as :ref:`doc_guidelines`.  This type of internal cross reference works across 
multiple files, and the linking text is obtained from the document source so if the title changes,
the link text will update as well.  (You should not link to the .rst file directly since this will
fail when the content is converted to HTML for the website.)

You can also link directly to a heading in a document using the same technique.  For example, this
section uses this tagging:

.. code-block:: rst

   .. _internal-linking:
   
   Internal Cross-Reference Linking
   ================================

I can link to this section from any other .rst file in this document tree using ``:ref:`internal-linking``` 
and it will show up as :ref:`internal-linking`.


Non-ASCII Characters
====================

You can insert non-ASCII characters such as a Trademark symbol, use the notation ``|trade|``.
These replacement names are defined in an include file used during the sphinx processing
of the reST files.  The names of these replacement characters are the same as used in HTML
entities used to insert characters in html, e.g., \&trade; and are defined in the
file ``sphinx_build/substitutions.txt`` and listed here:

.. literalinclude:: ../sphinx_build/substitutions.txt
   :language: rst


We've kept the substitutions list small but others can be added as needed.  (Note the use of :ltrim: 
in the substitutions include file to 
remove the required space between the "Ostro" word and the ``|trade|`` replacement code.)

Ostro |trade| Trademark
=======================

The Ostro |trade| name is a trademark of Intel Corporation and as such, there is a list of 
approved nouns that must follow the Ostro name in our documentation 
(and yes, "name" is one of the approved nouns). By far, the most common use is
"Ostro OS" or "Ostro Project". (In source code, this rule need not be followed for 
example, when using the Ostro name as part of a function of variable name.)

Use of non-approved nouns (or no noun at all) must be avoided, for example:

======================================  ========================================
It's incorrect to say:                  Instead say:
======================================  ========================================
"an Ostro device"                       "a device running Ostro OS"
"Ostro enables fast IoT development"    "Ostro OS enables fast IoT development"
======================================  ========================================

Here is a list of approved nouns:

===============================  ===============================  ===============================  
application framework            microkernel                      project
architecture                     name                             SDK
components                       nanokernel                       software
DDK                              operating system                 software development kit
device driver kit                OS                               tools
kernel                           package                          trademark
libraries                        platform
mark                             programming interface
===============================  ===============================  ===============================  
