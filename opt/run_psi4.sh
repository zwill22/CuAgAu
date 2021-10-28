#!/bin/bash

nproc=${1}
hours=${2}
files=${3}

functionals=(GAM M11-D3BJ MN15-D3BJ SCAN-D3BJ)

cwd=$PWD
for xc in ${functionals[@]}; do
  echo ${xc}
  cd ${xc}
  ../"$( dirname -- ${BASH_SOURCE[0]} )"/run-dir_psi4.py ${nproc} ${hours} . ${files}
  cd ..
done
