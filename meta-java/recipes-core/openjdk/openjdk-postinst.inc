# handles all postinst action for openjdk

pkg_postinst_${JDKPN}-vm-shark () {
        if grep -q "\-server ERROR" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg && ! grep -q "KNOWN" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg; then
          sed -i -e "/\-shark.*/d" -e "s|\(^\-server*\)|\-shark KNOWN\n\1|" -e "/^$/d" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
	else
          sed -i -e "s/\-shark.*/\-shark KNOWN/" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
        fi
}

pkg_prerm_${JDKPN}-vm-shark () {
	sed -i -e "/^\-shark.*/d" -e "/^$/d" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
        if grep -q "KNOWN" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg && grep -q "\-server ERROR" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg; then
          FIRST_KNOWN=`grep "KNOWN" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg | head -1`
          sed -i -e "/${FIRST_KNOWN}/d" -e  "s|\(^\-server*\)|${FIRST_KNOWN}\n\1|" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
        fi

        echo "-shark ERROR" >> ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
}

pkg_postinst_${JDKPN}-vm-cacao () {
        if grep -q "\-server ERROR" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg && ! grep -q "KNOWN" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg; then
          sed -i -e "/\-cacao.*/d" -e "s|\(^\-server*\)|\-cacao KNOWN\n\1|" -e "/^$/d" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
	else
          sed -i -e "s/\-cacao.*/\-cacao KNOWN/" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
        fi
}

pkg_prerm_${JDKPN}-vm-cacao () {
	sed -i -e "/^\-cacao.*/d" -e "/^$/d" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
        if grep -q "KNOWN" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg && grep -q "\-server ERROR" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg; then
          FIRST_KNOWN=`grep "KNOWN" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg | head -1`
          sed -i -e "/${FIRST_KNOWN}/d" -e  "s|\(^\-server*\)|${FIRST_KNOWN}\n\1|" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
        fi

        echo "-cacao ERROR" >> ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
}

pkg_postinst_${JDKPN}-vm-jamvm () {
        if grep -q "\-server ERROR" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg && ! grep -q "KNOWN" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg; then
          sed -i -e "/\-jamvm.*/d" -e "s|\(^\-server*\)|\-jamvm KNOWN\n\1|" -e "/^$/d" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
	else
          sed -i -e "s/\-jamvm.*/\-jamvm KNOWN/" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
        fi
}

pkg_prerm_${JDKPN}-vm-jamvm () {
	sed -i -e "/^\-jamvm.*/d" -e "/^$/d" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
        if grep -q "KNOWN" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg && grep -q "\-server ERROR" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg; then
          FIRST_KNOWN=`grep "KNOWN" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg | head -1`
          sed -i -e "/${FIRST_KNOWN}/d" -e  "s|\(^\-server*\)|${FIRST_KNOWN}\n\1|" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
        fi

        echo "-jamvm ERROR" >> ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
}

pkg_postinst_${JDKPN}-vm-zero () {
        if grep -q "KNOWN" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg && grep -q "\-server ERROR" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg; then
           FIRST_KNOWN=`grep "KNOWN" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg | head -1`
           sed -i -e "/${FIRST_KNOWN}/d" -e "/^$/d" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
           echo ${FIRST_KNOWN} >> $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
        fi

        sed -i -e "s|^\-server.*|\-server KNOWN|" -e "/^$/d" $D/${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
}

pkg_prerm_${JDKPN}-vm-zero () {
	sed -i -e "/^\-server.*/\-server ERROR" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
        if grep -q "KNOWN" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg; then
          FIRST_KNOWN=`grep "KNOWN" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg | head -1`
          sed -i -e "/${FIRST_KNOWN}/d" -e  "s|\(^\-server*\)|${FIRST_KNOWN}\n\1|" ${JDK_HOME}/jre/lib/${JDK_ARCH}/jvm.cfg
        fi
}

inherit update-alternatives

ALTERNATIVE_${JDKPN}-jre = "java"
ALTERNATIVE_TARGET_${JDKPN}-jre = "${JDK_HOME}/jre/bin/java"

ALTERNATIVE_${JDKPN}-jdk = "javac"
ALTERNATIVE_TARGET_${JDKPN}-jdk = "${JDK_HOME}/bin/javac"

ALTERNATIVE_LINK_NAME[java] = "${bindir}/java"
ALTERNATIVE_LINK_NAME[javac] = "${bindir}/javac"

