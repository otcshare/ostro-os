# handles all postinst action for openjdk

# some of the former results in a build error because "ERR" is in the first line.

pkg_postinst_${JDKPN}-vm-shark () {
    true
    if grep -q "\-server ERROR" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg && ! grep -q "KNOWN" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg; then
        sed -i -e "/\-shark.*/d" -e "s|\(^\-server*\)|\-shark KNOWN\n\1|" -e "/^$/d" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
    else
        sed -i -e "s/\-shark.*/\-shark KNOWN/" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
    fi
}

pkg_prerm_${JDKPN}-vm-shark () {
    true
    sed -i -e "/^\-shark.*/d" -e "/^$/d" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
    if grep -q "KNOWN" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg && grep -q "\-server ERROR" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg; then
        FIRST_KNOWN=`grep "KNOWN" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg | head -n 1`
        sed -i -e "/${FIRST_KNOWN}/d" -e  "s|\(^\-server*\)|${FIRST_KNOWN}\n\1|" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
    fi

    echo "-shark ERROR" >> ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
}

pkg_postinst_${JDKPN}-vm-cacao () {
    true
    if grep -q "\-server ERROR" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg && ! grep -q "KNOWN" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg; then
        sed -i -e "/\-cacao.*/d" -e "s|\(^\-server*\)|\-cacao KNOWN\n\1|" -e "/^$/d" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
    else
        sed -i -e "s/\-cacao.*/\-cacao KNOWN/" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
    fi
}

pkg_prerm_${JDKPN}-vm-cacao () {
    true
    sed -i -e "/^\-cacao.*/d" -e "/^$/d" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
    if grep -q "KNOWN" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg && grep -q "\-server ERROR" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg; then
        FIRST_KNOWN=`grep "KNOWN" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg | head -n 1`
        sed -i -e "/${FIRST_KNOWN}/d" -e  "s|\(^\-server*\)|${FIRST_KNOWN}\n\1|" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
    fi

    echo "-cacao ERROR" >> ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
}

pkg_postinst_${JDKPN}-vm-jamvm () {
    true
    if grep -q "\-server ERROR" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg && ! grep -q "KNOWN" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg; then
        sed -i -e "/\-jamvm.*/d" -e "s|\(^\-server*\)|\-jamvm KNOWN\n\1|" -e "/^$/d" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
    else
        sed -i -e "s/\-jamvm.*/\-jamvm KNOWN/" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
    fi
}

pkg_prerm_${JDKPN}-vm-jamvm () {
    true
    sed -i -e "/^\-jamvm.*/d" -e "/^$/d" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
    if grep -q "KNOWN" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg && grep -q "\-server ERROR" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg; then
        FIRST_KNOWN=`grep "KNOWN" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg | head -n 1`
        sed -i -e "/${FIRST_KNOWN}/d" -e  "s|\(^\-server*\)|${FIRST_KNOWN}\n\1|" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
    fi

    echo "-jamvm ERROR" >> ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
}

pkg_postinst_${JDKPN}-vm-zero () {
    true
    if grep -q "KNOWN" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg && grep -q "\-server ERROR" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg; then
        FIRST_KNOWN=`grep "KNOWN" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg | head -n 1`
        sed -i -e "/${FIRST_KNOWN}/d" -e "/^$/d" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
        echo ${FIRST_KNOWN} >> $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
    fi

    sed -i -e "s|^\-server.*|\-server KNOWN|" -e "/^$/d" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
}

pkg_prerm_${JDKPN}-vm-zero () {
    true
    sed -i -e "/^\-server.*/\-server ERROR" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
    if grep -q "KNOWN" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg; then
        FIRST_KNOWN=`grep "KNOWN" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg | head -n 1`
        sed -i -e "/${FIRST_KNOWN}/d" -e  "s|\(^\-server*\)|${FIRST_KNOWN}\n\1|" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
    fi
}

pkg_postinst_${JDKPN}-jre () {
    ln -s ${JDK_HOME}/jre  $D/${libdir}/jvm/jre
}

inherit update-alternatives

ALTERNATIVE_${JDKPN}-jre = "java keytool"
ALTERNATIVE_${JDKPN}-jdk = "javac"

ALTERNATIVE_TARGET[java] = "${JDK_HOME}/jre/bin/java"
ALTERNATIVE_TARGET[javac] = "${JDK_HOME}/bin/javac"
ALTERNATIVE_TARGET[keytool] = "${JDK_HOME}/jre/bin/keytool"

ALTERNATIVE_LINK_NAME[java] = "${bindir}/java"
ALTERNATIVE_LINK_NAME[javac] = "${bindir}/javac"
ALTERNATIVE_LINK_NAME[keytool] = "${bindir}/keytool"
