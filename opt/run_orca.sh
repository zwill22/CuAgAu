#!/bin/bash

nproc=${1}
hours=${2}
files=${3}

functionals=(B2PLYP-D3BJ TPSSh-D3BJ TPSS-D3BJ DSD-BLYP-D3BJ M06-D3 wB97X-V wB97M-V)

cwd=$PWD
cd "$( dirname -- ${BASH_SOURCE[0]} )"
bashsrc=$PWD
cd $cwd
echo ${bashsrc}

for xc in ${functionals[@]}; do
  echo ${xc}
  cd ${xc}
  python "${bashsrc}"/run-dir_orca.py ${nproc} ${hours} . ${files}
  cd ..
done
