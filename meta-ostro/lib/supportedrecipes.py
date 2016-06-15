# Python code implementing most of the logic behind
# supported-recipes.bbclass.

import csv
import os
import re
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse
import pkgutil
import inspect

import bb
import supportedrecipesreport

class Columns(object):
    """Base class for all classes which extend the SUPPORTED_RECIPES_SOURCES report.

    Typically used to add columns, hence the name. Usage of the class is:
    - instantiated when starting to write a report
    - extend_header() - add new columns
    - extend_row() - add data for new colums to each row as it is getting written

    To add new classes, create a "lib/supportedrecipesreport" directory in your layer,
    with an empty "__init__.py" file and one or more classes inheriting from this base
    class defined in one or more regular .py files.
    """
    def __init__(self, d, all_rows):
        """Initialize instance.

        Gets access to the global datastore and all rows that are to be written (unmodified
        and read-only).
        """
        pass

    def extend_header(self, row_headers):
        """Add new columns.

        Called with a list of field names, in the order in which the
        resultig .cvs report will have them.  extend_header() then may
        extend the list of fields. See supportedrecipes.py for
        a list of already present fields.
        """
        pass

    def extend_row(self, row):
        """Add data for new columns or modify existing ones.

        Called with a hash mapping field names to the corresponding data.
        """
        pass

def parse_regex(regex, filename, linenumber):
    try:
        # must match entire string, hence the '$'
        return (re.compile(regex + '$'), regex)
    except Exception as ex:
        raise RuntimeError("%s.%d: parsing '%s' as regular expression failed: %s" % (
            filename,
            linenumber,
            regex,
            str(ex)))

class SupportedRecipe:
    def __init__(self, pattern, filename, linenumber):
        self.filename = filename
        self.pattern = pattern
        self.linenumber = linenumber
        parts = pattern.split('@')
        if len(parts) != 2:
            raise RuntimeError("%s.%d: entry must have format <recipe name regex>@<collection name regex>, "
                               "splitting by @ found %d parts instead: %s" %
                               (filename, linenumber, len(parts), pattern))
        self.pn_re = parse_regex(parts[0], filename, linenumber)
        self.collection_re = parse_regex(parts[1], filename, linenumber)

    def supported(self, pn, collection):
        supported = bool((pn is None or self.pn_re[0].match(pn)) and
                         (collection is None or self.collection_re[0].match(collection)))
        return supported

class SupportedRecipes:
    def __init__(self):
        self.supported = []

    def append(self, recipe):
        self.supported.append(recipe)

    def current_recipe_supported(self, d):
        pn = d.getVar('PN', True)
        filename = d.getVar('FILE', True)
        collection = bb.utils.get_file_layer(filename, d)
        return self.recipe_supported(pn, collection)

    def recipe_supported(self, pn, collection):
        return any((supported_recipe.supported(pn, collection)
                    for supported_recipe in self.supported))


def load_supported_recipes(d):

    files = []
    supported_files = d.getVar('SUPPORTED_RECIPES', True)
    if not supported_files:
        bb.fatal('SUPPORTED_RECIPES is not set')
    supported_recipes = SupportedRecipes()
    for filename in supported_files.split():
        try:
            with open(filename) as f:
                linenumber = 1
                for line in f:
                    if line.startswith('#'):
                        continue
                    # TODO (?): sanity check the content to catch
                    # obsolete entries or typos.
                    pn = line.strip()
                    if pn:
                        supported_recipes.append(SupportedRecipe(line.strip(),
                                                                 filename,
                                                                 linenumber))
                    linenumber += 1
            files.append(filename)
        except OSError as ex:
            bb.fatal('Could not read SUPPORTED_RECIPES = %s: %s' % (supported_files, str(ex)))

    return (supported_recipes, files)

SOURCE_FIELDS = 'component,collection,version,homepage,source,summary'.split(',')

# Collects information about one recipe during parsing for SUPPORTED_RECIPES_SOURCES.
# The dumped information cannot be removed because it might be needed in future
# bitbake invocations, so the default location is inside the tmp directory.
def dump_sources(d):
    pn = d.getVar('PN', True)
    filename = d.getVar('FILE', True)
    collection = bb.utils.get_file_layer(filename, d)
    pv = d.getVar('PV', True)
    summary = d.getVar('SUMMARY', True) or ''
    homepage = d.getVar('HOMEPAGE', True) or ''
    src = d.getVar('SRC_URI', True).split()
    sources = []
    for url in src:
        scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
        if scheme != 'file':
            parts = path.split(';')
            if len(parts) > 1:
                path = parts[0]
                params = dict([x.split('=') if '=' in x else (x, '') for x in parts[1:]])
            else:
                params = {}
            name = params.get('name', None)
            sources.append((name, '%s://%s%s' % (scheme, netloc, path)))
    dumpfile = d.getVar('SUPPORTED_RECIPES_SOURCES_DIR', True) + '/' + pn + filename
    bb.utils.mkdirhier(os.path.dirname(dumpfile))
    with open(dumpfile, 'w') as f:
        # File intentionally kept small by not writing a header
        # line. Guaranteed to contain SOURCE_FIELDS.
        writer = csv.writer(f)
        for idx, val in enumerate(sources):
            name, url = val
            if name and len(sources) != 1:
                fullname = '%s/%s' % (pn, name)
            elif idx > 0:
                fullname = '%s/%d' % (pn, idx)
            else:
                fullname = pn
            writer.writerow((fullname, collection, pv, homepage, url, summary))

class IsNative(object):
    def __init__(self, d):
        # Always add a trailing $ to ensure a full match.
        native_recipes = d.getVar('SUPPORTED_RECIPES_NATIVE_RECIPES', True).split()
        self.isnative_exception = re.compile('(' + '|'.join(native_recipes) + ')$')
        self.isnative_baseclasses = d.getVar('SUPPORTED_RECIPES_NATIVE_BASECLASSES', True).split()

    def __call__(self, pn, pndata):
        for inherited in pndata['inherits']:
            if os.path.basename(inherited) in self.isnative_baseclasses:
                return True
        # Some build recipes do not inherit cross.bbclass and must be skipped explicitly.
        # The "real" recipes (in cases like glibc) still get checked. Other recipes are OE-core
        # internal helpers.
        if self.isnative_exception.match(pn):
            return True

class TruncatedError(Exception):
    pass

def dump_dependencies(depgraph, max_lines, unsupported):
    # Walk the recipe dependency tree and add one line for each path that ends in
    # an unsupported recipe.
    lines = []
    current_line = []

    # Pre-compute complete dependencies (DEPEND and RDEPEND) for each recipe
    # instead of doing it each time we reach a recipe. Also identifies those
    # recipes that nothing depends on. They are the start points for the build.
    roots = set(depgraph['pn'])
    deps = {}
    for task, taskdeps in depgraph['tdepends'].items():
        pn = task.split('.')[0]
        pndeps = deps.setdefault(pn, set())
        for taskdep in taskdeps:
            pndep = taskdep.split('.')[0]
            if pndep != pn:
                pndeps.add(pndep)
                roots.discard(pndep)
    for pn in deps:
        deps[pn] = sorted(deps[pn])

    # We can prune the search tree a lot by keeping track of those recipes which are already
    # known to not depend on an unsupported recipe.
    okay = set()

    def visit_recipe(pn):
        if pn in okay:
            return False
        if pn in current_line:
            # Recursive dependency, bail out. Can happen
            # because we flattened the task dependencies; those don't have
            # cycles.
            return False
        current_line.append(pn)
        printed = False
        for dep in deps.get(pn, []):
            if visit_recipe(dep):
                printed = True
        if not printed and \
           pn in unsupported and \
           not len(current_line) == 1:
            # Current path is non-trivial, ends in an unsupported recipe and was not alread
            # included in a longer, printed path. Add a copy to the output.
            if len(lines) >= max_lines:
                raise TruncatedError()
            lines.append(current_line[:])
            printed = True
        if not printed and not pn in unsupported:
            okay.add(pn)
        del current_line[-1]
        return printed

    truncated = False
    try:
        for pn in sorted(roots):
            visit_recipe(pn)
    except TruncatedError:
        truncated = True
    return lines, truncated

def collection_hint(pn, supported_recipes):
    # Determines whether the recipe would be supported in some other collection.
    collections = set([supported_recipe.collection_re[1]
                       for supported_recipe
                       in supported_recipes.supported
                       if supported_recipe.supported(pn, None)])
    return ' (would be supported in %s)' % ' '.join(collections) if collections else ''

def dump_unsupported(unsupported, supported_recipes):
    # Turns the mapping from unsupported recipe to is collection
    # into a sorted list of entries in the final report.
    lines = []
    for pn, collection in unsupported.items():
        # Left and right side of the <recipe>@<collection> entries are
        # regular expressions. In contrast to re.escape(), we only
        # escape + (as in gtk+3). Escaping all non-alphanumerics
        # makes many entries (like linux-yocto) unnecessarily less
        # readable (linux\-yocto).
        pn = pn.replace('+', r'\+')
        collection = collection.replace('+', r'\+')
        hint = collection_hint(pn, supported_recipes)
        entry = '%s@%s%s' % (pn, collection, hint)
        lines.append(entry)
    return sorted(lines)

def check_build(d, event):
    supported_recipes, files = load_supported_recipes(d)
    supported_recipes_check = d.getVar('SUPPORTED_RECIPES_CHECK', True)
    if not supported_recipes_check:
        return

    isnative = IsNative(d)
    valid = ('note', 'warn', 'error', 'fatal')
    if supported_recipes_check not in valid:
        bb.fatal('SUPPORTED_RECIPES_CHECK must be set to one of %s, currently is: %s' %
                 ('/'.join(valid), supported_recipes_check))
    logger = bb.__dict__[supported_recipes_check]

    # See bitbake/lib/bb/cooker.py buildDependTree() for the content of the depgraph hash.
    # Basically it mirrors the information dumped by "bitbake -g".
    depgraph = event._depgraph
    # import pprint
    # bb.note('depgraph: %s' % pprint.pformat(depgraph))

    dirname = d.getVar('SUPPORTED_RECIPES_SOURCES_DIR', True)
    report_sources = d.getVar('SUPPORTED_RECIPES_SOURCES', True)

    unsupported = {}
    sources = []
    for pn, pndata in depgraph['pn'].items():
        # We only care about recipes compiled for the target.
        # Most native ones can be detected reliably because they inherit native.bbclass,
        # but some special cases have to be hard-coded.
        # Image recipes also do not matter.
        if not isnative(pn, pndata):
            filename = pndata['filename']
            collection = bb.utils.get_file_layer(filename, d)
            supported = supported_recipes.recipe_supported(pn, collection)
            if not supported:
                unsupported[pn] = collection
            if report_sources:
                dumpfile = os.path.join(dirname, pn + filename)
                with open(dumpfile) as f:
                    reader = csv.reader(f)
                    for row in reader:
                        row_hash = {f: row[i] for i, f in enumerate(SOURCE_FIELDS)}
                        row_hash['supported'] = 'yes' if supported else 'no'
                        sources.append(row_hash)

    if report_sources:
        with open(report_sources, 'w') as f:
            fields = SOURCE_FIELDS[:]
            # Insert after 'collection'.
            fields.insert(fields.index('collection') + 1, 'supported')
            extensions = []
            for importer, modname, ispkg in pkgutil.iter_modules(supportedrecipesreport.__path__):
                module = __import__('supportedrecipesreport.' + modname, fromlist="dummy")
                for name, clazz in inspect.getmembers(module, inspect.isclass):
                    if issubclass(clazz, Columns):
                        extensions.append(clazz(d, sources))
            for e in extensions:
                e.extend_header(fields)
            writer = csv.DictWriter(f, fields)
            writer.writeheader()
            for row in sources:
                for e in extensions:
                    e.extend_row(row)
            # Sort by first column, then second column, etc., after extending all rows.
            for row in sorted(sources, key=lambda r: [r.get(f, None) for f in fields]):
                writer.writerow(row)
        bb.note('Created SUPPORTED_RECIPES_SOURCES = %s file.' % report_sources)

    if unsupported:
        max_lines = int(d.getVar('SUPPORTED_RECIPES_CHECK_DEPENDENCY_LINES', True))
        dependencies, truncated = dump_dependencies(depgraph, max_lines, unsupported)

        output = []
        output.append('The following unsupported recipes are required for the build:')
        output.extend(['  ' + line for line in dump_unsupported(unsupported, supported_recipes)])
        output.append('''
Each unsupported recipe is identified by the recipe name and the collection
in which it occurs and has to be marked as supported (see below) using that
format. Typically each layer has exactly one collection.''')
        if dependencies:
            # Add the optional dependency dump.
            output.append('''
Here are the dependency chains (including DEPENDS and RDEPENDS)
which include one or more of the unsupported recipes. -> means "depends on"
and * marks unsupported recipes:''')
            for line in dependencies:
                line_entries = [('*' if pn in unsupported else '') + pn for pn in line]
                output.append('  ' + ' -> '.join(line_entries))
            if truncated:
                output.append('''...
Output truncated, to see more increase SUPPORTED_RECIPES_CHECK_DEPENDENCY_LINES (currently %d).''' %
                              max_lines)

        output.append('''
To avoid this message, several options exist:
* Check the dependency chain(s) to see why a recipe gets pulled in and perhaps
  change recipe configurations or image content to avoid pulling in undesired
  components.
* If the recipe is supported in some other layer, disable the unsupported one
  with BBMASK.
* Add the unsupported recipes to one of the following files:
  %s
  Regular expressions are supported on both sides of the @ separator.
* Create a new file which lists the unsupported recipes and extend SUPPORTED_RECIPES:
    SUPPORTED_RECIPES_append = " <path>/recipes-supported-by-me.txt"
  See meta-ostro/conf/layer.conf and ostro.conf for an example how the path can be
  derived automatically. The expectation is that SUPPORTED_RECIPES gets set in
  distro configuration files, depending on the support provided by the distro
  creator.
* Disable the check with SUPPORTED_RECIPES_CHECK = "" in local.conf.
  'bitbake -g <build target>' produces .dot files showing these dependencies.
''' % '\n  '.join(files))

        logger('\n'.join(output))
