#!/bin/bash

KS_TMP=/tmp/canvas-ks-import-$RANDOM

KS_PATH=${1:-"/data/store/store/src/kororaproject/spin-kickstarts.git"}
VERSION=${2:-}

mkdir ${KS_TMP}

for KS in "fedora-live-base.ks" "fedora-live-kde.ks" "fedora-live-cinnamon.ks" "fedora-live-workstation.ks" "fedora-live-mate_compiz.ks" "fedora-live-xfce.ks"
do
  _IN="${KS_PATH}/${KS}"
  _OUT="${KS_TMP}/${KS}"

  # check we can read the ks file
  [ -r ${_IN} ] || continue

  pushd ${KS_PATH} >/dev/null 2>&1
  ksflatten -c ${_IN} -o ${_OUT} >/dev/null 2>&1
  popd >/dev/null 2>&1

  _NAME=${KS/workstation/gnome}
  _NAME=${_NAME%%.ks}

  if [ "x${VERSION}" != "x" ];
  then
    _NAME="${_NAME}:${VERSION}"
  fi

  echo  PYTHONPATH=./lib canvas template update kororaproject:${_NAME} --from-kickstart ${_OUT}
done

rm -rf ${KS_TMP}
