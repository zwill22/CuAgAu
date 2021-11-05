#!/bin/bash

nproc=${1}
hours=${2}
files=${3}

functionals=(GAM M11-D3BJ MN15-D3BJ SCAN-D3BJ)

cwd=$PWD
cd "$( dirname -- ${BASH_SOURCE[0]} )"
bashsrc=$PWD
cd $cwd
echo ${bashsrc}

for xc in ${functionals[@]}; do
  echo ${xc}
  cd ${xc}
  python "${bashsrc}"/run-dir_psi4.py ${nproc} ${hours} . ${files}
  cd ..
done
