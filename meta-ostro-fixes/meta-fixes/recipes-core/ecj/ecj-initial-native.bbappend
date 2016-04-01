do_compile() {
  # Create the start script
  echo "#!/bin/sh" > ecj-initial

  # get absolute path to parent directory, and use that as base path for the jar
  echo "SH_DIR=\`dirname "\$0"\`" >> ecj-initial
  echo "CURRENT_DIR=\`cd "\${SH_DIR}" && pwd\`" >> ecj-initial
  echo "PARENT_DIR=\`dirname \${CURRENT_DIR}\`" >> ecj-initial

  echo "ECJ_JAR=\${PARENT_DIR}/share/java/${JAR}" >> ecj-initial
  echo "RUNTIME=java-initial" >> ecj-initial
  cat ecj-initial.in >> ecj-initial
}
