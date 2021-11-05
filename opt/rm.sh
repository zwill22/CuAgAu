#!/bin/bash

functionals=(B3LYP-D3BJ BLYP-D3BJ B-LYP-osUW12-D3BJ CAM-B3LYP-D3BJ PBE0-D3BJ PBE-D3BJ wB97X-D3 WM21-D3BJ XCH-BLYP-UW12-D3BJ)

for xc in ${functionals[@]}; do
  rm ${xc}/Cu01N0_H.out
done
