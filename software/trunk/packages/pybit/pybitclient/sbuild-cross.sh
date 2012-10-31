#!/bin/sh

set -e

DSC=`find / -name ${SBUILD_BUILD_DSC_File}`
DIR=`dirname ${DSC}`
cd ${DIR}
dpkg-source -x ${DSC}
cd ${SBUILD_BUILD_DSC_Dir}
embuilddeps -a armel
