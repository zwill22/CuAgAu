#!/bin/bash

for folder in */; do
	echo ${folder};
	cd ${folder};
	for file in *.in; do
		if [ ! -f ${file%.in}.out ]; then
			echo "${file} - Result missing";
		elif `grep -q 'End time' ${file%.in}.out`; then
			true;
		elif `grep -q 'ORCA TERMINATED NORMALLY' ${file%.in}.out`; then
			 true;
		elif `grep -q -i "SCF not converged" ${file%.in}.out`; then
			echo "${file} - SCF not converged";
		elif `grep -q "doesn't contain an entry for element" ${file%.in}.out`; then
			echo "${file} - Incomplete basis set";
		elif `grep -q "not aligned to z axis" ${file%.in}.out`; then
			if `grep -q "Total Enthalpy" ${file%.in}.out`; then
                        	true
                        else
				echo "${file} - Z axis alignment issue";
			fi
		elif `grep -q "Psi4 encountered an error" ${file%.in}.out`; then
			echo "${file} - Psi4 error";
		elif `grep -q "Error: largest angular momentum" ${file%.in}.out`; then
			echo "${file} - Angular momentum error";
		else
			echo "${file} - Calculation incomplete";
		fi;
	done;
	cd ..;
done
