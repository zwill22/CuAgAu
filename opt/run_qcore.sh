#!/bin/bash

nproc=${1}
hours=${2}
files=${3}

functionals=(B3LYP-D3BJ BLYP-D3BJ B-LYP-osUW12-D3BJ CAM-B3LYP-D3BJ PBE0-D3BJ PBE-D3BJ wB97X-D3 WM21-D3BJ XCH-BLYP-UW12-D3BJ)

cwd=$PWD
for xc in ${functionals[@]}; do
  echo ${xc}
  cd ${xc}
  ${HOME}/gmtkn30/scripts/run-dir.sh ${nproc} ${hours} . ${files}
  cd ..
done
