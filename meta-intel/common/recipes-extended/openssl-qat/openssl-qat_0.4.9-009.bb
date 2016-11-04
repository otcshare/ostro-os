include openssl-qat.inc

OPENSSL_VERSION = "1.0.1async"

SRC_URI  += "git://opensslfoundation.com/openssl-async.git;branch=OpenSSL_1_0_1-async;rev=asynch_v0.4.9-009 \
             file://openssl-qat_0.4.9-009-openssl_qat-add-version-script.patch \
             file://openssl-qat_0.4.9-009-openssl_qat-add-openssl-async-specific-symbols.patch \
             "

SRC_URI[openssl_qat.md5sum]="8e2b45cf9b345356bdff0956845c6103"
SRC_URI[openssl_qat.sha256sum]="c2334b4d1fc8498e06f0554ef155041a6bf441de134cfdd3635e5a449a34bf81"

