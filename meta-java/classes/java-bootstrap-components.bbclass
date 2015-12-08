# This is to be used by recipes which rely on java-library.bbclass
# infrastructure and their a *-native recipe are parts of the bootstrap
# process
#

DEPENDS_prepend_class-native = " ecj-bootstrap-native "
DEPENDS_prepend_class-target = " virtual/javac-native "
