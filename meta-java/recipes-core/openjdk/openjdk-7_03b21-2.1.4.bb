require openjdk-7-release-03b21.inc

PR = "${INC_PR}.0"

ICEDTEA = "icedtea-2.1.4"

SRC_URI[iced.md5sum] = "7d1adfad5cc7f98a57712a5c5e11e1a1"
SRC_URI[iced.sha256sum] = "7762ce53479e49f8afffc81621515eb6c3f765c578ff13d4c601ce4af8935db6"

HOTSPOT_CHANGESET = "3f345e5f65eb"
SRC_URI[hotspot.md5sum] = "c995de20564762bd8b9c820d1a7107ca"
SRC_URI[hotspot.sha256sum] = "fa482a6ace16f95dd53cb99c842da401e634a4536ef1a18280e5d3b7843954b0"

CORBA_CHANGESET = "fccd14ecf86c"
SRC_URI[corba.md5sum] = "db118d8f30d478758bb9544bc6722d60"
SRC_URI[corba.sha256sum] = "bc761a960972906ec67b208e94f557bd9d1ceb07ae9020776a4774674d57ff44"

JAXP_CHANGESET = "fb08c190f504"
SRC_URI[jaxp.md5sum] = "1edd4f7bb4623bb42fb10553bcf2c922"
SRC_URI[jaxp.sha256sum] = "619254245e5876614689c95cff44124462252bc0c074c85c657a1bac76e04043"

JAXWS_CHANGESET = "77e7849c5e50"
SRC_URI[jaxws.md5sum] = "c05e26c9d0265dd70da03c749d3e56df"
SRC_URI[jaxws.sha256sum] = "4a60a1af32b4a274579e9932b22d552df6aae00640a3caf6a27109bdc2fe5d5a"

JDK_CHANGESET = "e7d1cb36e005"
SRC_URI[jdk.md5sum] = "01f5e22d4f3530a887b7c186d9adeae5"
SRC_URI[jdk.sha256sum] = "1397d8e1f15fb6cb28a8c37fe15c93f8b95d36d5a4c6753cf621d28af620d6bf"

LANGTOOLS_CHANGESET = "de674a569978"
SRC_URI[langtools.md5sum] = "bfe0e37cbdd3281a66897c1180f47aa0"
SRC_URI[langtools.sha256sum] = "b8c28b2de175694d1b8d6ff94c5ba616250aa3f39f41123e188cfec0b0a14da8"

OPENJDK_CHANGESET = "bc612c7c99ec"
SRC_URI[openjdk.md5sum] = "ec5caa23f2d3f1622b11c56869a0aa4f"
SRC_URI[openjdk.sha256sum] = "d1953daabbae4efdd61a4c670c1b9d28c595307ff226e13b04dcf989d699fbcf"
