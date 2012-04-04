DESCRIPTION = "GNU Classpath standard Java libraries - For native Java-dependent programs"
HOMEPAGE = "http://www.gnu.org/software/classpath/"
LICENSE = "Classpath"

DEPENDS = "ecj-initial fastjar-native zip-native gettext-native"

PR = "r1"

inherit autotools native

SRC_URI = "${GNU_MIRROR}/classpath/classpath-${PV}.tar.gz"

do_configure_prepend () {

	cp ${STAGING_DATADIR_NATIVE}/gettext/config.rpath ${S}
}

export JAVA="${STAGING_BINDIR_NATIVE}/java-initial"
export JAVAC="${STAGING_BINDIR_NATIVE}/ecj-initial"
export JAVACFLAGS="-nowarn"

EXTRA_OECONF = " \
                --with-glibj \
                --enable-local-sockets \
                --disable-Werror \
                --disable-alsa \
                --disable-gconf-peer \
                --disable-gtk-peer \
                --disable-plugin \
                --disable-dssi \
                --disable-gjdoc \
                --disable-examples \
                --enable-tools \
                --includedir=${STAGING_INCDIR}/classpath \
               "

