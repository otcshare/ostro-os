DESCRIPTION = "A pure Java D-Bus Implementation"
DESCRIPTION_${PN}-viewer = "${DESCRIPTION} (DBusViewer Binary)"
DESCRIPTION_${PN}-bin = "${DESCRIPTION} (Binaries)"
AUTHOR = "Matthew Johnson <dbus@matthew.ath.cx>"
HOMEPAGE = "http://dbus.freedesktop.org/doc/dbus-java"
SECTION = "libs"
LICENSE = "LGPL-2.1 & AFL-2.1"

DEPENDS = "libmatthew docbook-utils-native docbook-sgml-dtd-4.1-native fastjar-native"
RDEPENDS_${PN}-viewer = "java2-runtime libunixsocket-java ${PN}-bin libmatthew-debug-java ${JPN}"
RDEPENDS_${PN}-bin = "java2-runtime libunixsocket-java libmatthew-debug-java ${JPN}"
RSUGGESTS_${JPN} = "libunixsocket-java"

PR = "r0"
LIC_FILES_CHKSUM = "file://COPYING;md5=72cc739fb93ae32741edbae802490e92"
SRC_URI = "http://dbus.freedesktop.org/releases/dbus-java/dbus-java-${PV}.tar.gz"

SRC_URI[md5sum] = "8b8470db5cd657591bac245e3b6e18e4"
SRC_URI[sha256sum] = "be404ea36284d938646192d0ee42e146853064217d4e3aaf89b56bd351ebca33"

S = "${WORKDIR}/dbus-java-${PV}"

inherit java-library

# jamvm-native unfortunately contains non-generificed java/lang/reflect classes
# which are accessed in this package. Work around this by setting the bootclasspath
# explicitly.
#JCFLAGS = "-bootclasspath ${STAGING_DATADIR}/classpath/glibj.zip"

do_compile () {
  oe_runmake \
	JCFLAGS="-source 1.5 ${JCFLAGS}" \
	JAVAC="javac" \
	JARPREFIX="${STAGING_DATADIR_JAVA}" \
	JAVAUNIXJARDIR="${STAGING_DATADIR_JAVA}" \
	JAVAUNIXLIBDIR="${STAGING_DIR_TARGET}${libdir_jni}" \
	CLASSPATH="${S}/classes" \
	JAR="fastjar" \
	bin

  # Generated shell scripts will have staging paths inside them.
	rm bin/*

	# Generate them again with target paths.
	oe_runmake \
		JAVAC="oefatal \"No Java compilation expected here.\"" \
		JAR="oefatal \"No jar invocation expected here.\"" \
		JARPREFIX=${datadir_java} \
		JAVAUNIXJARDIR=${datadir_java} \
		JAVAUNIXLIBDIR=${libdir_jni} \
		bin

	# Generate man pages.
	oe_runmake \
		JAVAC="oefatal \"No Java compilation expected here.\"" \
		JAR="oefatal \"No jar invocation expected here.\"" \
		JARPREFIX=${datadir_java} \
		JAVAUNIXJARDIR=${datadir_java} \
		JAVAUNIXLIBDIR=${libdir_jni} \
		man
}

JARFILENAME = "${JPN}-${PV}.jar"

do_install () {
  oe_jarinstall ${JPN}-${PV}.jar ${JPN}.jar dbus.jar
  oe_jarinstall dbus-java-viewer-${PV}.jar dbus-java-viewer.jar dbus-viewer.jar
  oe_jarinstall dbus-java-bin-${PV}.jar dbus-java-bin.jar dbus-bin.jar

  install -d ${D}${bindir}
  install bin/DBusViewer ${D}${bindir}
  install bin/DBusCall ${D}${bindir}
  install bin/CreateInterface ${D}${bindir}
  install bin/ListDBus ${D}${bindir}
  install bin/DBusDaemon ${D}${bindir}

	oe_runmake \
		JAVAC="oefatal \"No Java compilation expected here.\"" \
		JAR="oefatal \"No jar invocation expected here.\"" \
		MANPREFIX=${D}${mandir} \
		DOCPREFIX=${D}${docdir}/${JPN} \
		install-man
}

# ${JPN} must be last otherwise it would pick up dbus-viewer*.jar
# and dbus-bin*.jar
PACKAGES = "${PN}-viewer ${PN}-viewer-doc ${PN}-bin ${PN}-bin-doc ${JPN}"

FILES_${PN}-viewer = "${datadir}/java/dbus-java-viewer*.jar ${bindir}/DBusViewer"
FILES_${PN}-viewer-doc = "${mandir}/DBusViewer*"
FILES_${PN}-bin = "${datadir}/java/dbus-java-bin*.jar ${bindir}"
FILES_${PN}-bin-doc = "${mandir} ${docdir}/${JPN}"
