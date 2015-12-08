require openjdk-8-release-72b05.inc
require openjdk-8-native.inc

PROVIDES = "virtual/java-native virtual/javac-native"

inherit update-alternatives

ALTERNATIVE_${PN} = "java javac jar pack200 unpack200 keytool"
ALTERNATIVE_LINK[java] = "${bindir}/java"
ALTERNATIVE_TARGET[java] = "${JDK_HOME}/bin/java"
ALTERNATIVE_PRIORITY[java] = "100"
ALTERNATIVE_LINK[javac] = "${bindir}/javac"
ALTERNATIVE_TARGET[javac] = "${JDK_HOME}/bin/javac"
ALTERNATIVE_PRIORITY[javac] = "100"
ALTERNATIVE_LINK[jar] = "${bindir}/jar"
ALTERNATIVE_TARGET[jar] = "${JDK_HOME}/bin/jar"
ALTERNATIVE_PRIORITY[jar] = "100"
ALTERNATIVE_LINK[pack200] = "${bindir}/pack200"
ALTERNATIVE_TARGET[pack200] = "${JDK_HOME}/bin/pack200"
ALTERNATIVE_PRIORITY[pack200] = "100"
ALTERNATIVE_LINK[unpack200] = "${bindir}/unpack200"
ALTERNATIVE_TARGET[unpack200] = "${JDK_HOME}/bin/unpack200"
ALTERNATIVE_PRIORITY[unpack200] = "100"
ALTERNATIVE_LINK[keytool] = "${bindir}/keytool"
ALTERNATIVE_TARGET[keytool] = "${JDK_HOME}/bin/keytool"
ALTERNATIVE_PRIORITY[keytool] = "100"

# PR = "${INC_PR}.1"
