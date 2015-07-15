do_install_append() {
	cat >> ${D}${sysconfdir}/profile << EOT
JAVA_HOME=""
for dir in ${libdir}/jvm/*; do
	if [ -x "\${dir}/bin/java" ]; then
		[ -z "\${JAVA_HOME}" ] && JAVA_HOME="\${dir}"
	fi
done
if [ -n "\${JAVA_HOME}" ]; then
	export JAVA_HOME=\${JAVA_HOME}
fi
EOT
}
