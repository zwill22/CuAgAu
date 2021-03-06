#!/bin/bash

for folder in */; do
	cd ${folder};
	for file in *.in; do
		if [ ! -f ${file%.in}.out ]; then
			echo "${folder}${file} - Result missing";
		elif `grep -q 'End time' ${file%.in}.out`; then
			true;
		elif `grep -q 'ORCA TERMINATED NORMALLY' ${file%.in}.out`; then
			 true;
		elif `grep -q 'Psi4 exiting successfully' ${file%.in}.out`; then
			 true;
		elif `grep -q -i "SCF not converged" ${file%.in}.out`; then
			echo "${folder}${file} - SCF not converged";
		elif `grep -q -i "could not converge SCF" ${file%.in}.out`; then
			echo "${folder}${file} - SCF not converged";
		elif `grep -q -i "could not converge geometry opt" ${file%.in}.out`; then
			echo "${folder}${file} - Geometry not converged";
		elif `grep -q "doesn't contain an entry for element" ${file%.in}.out`; then
			echo "${folder}${file} - Incomplete basis set";
		elif `grep -q "not aligned to z axis" ${file%.in}.out`; then
			if `grep -q "Total Enthalpy" ${file%.in}.out`; then
                        	true
                        else
				echo "${folder}${file} - Z axis alignment issue";
			fi
		elif `grep -q "Fatal Error: Matrix::power" ${file%.in}.out`; then
			echo "${folder}${file} - Matrix error";
		elif `grep -q "Psi4 encountered an error" ${file%.in}.out`; then
			echo "${folder}${file} - Psi4 error";
		elif `grep -q "Error: largest angular momentum" ${file%.in}.out`; then
			echo "${folder}${file} - Angular momentum error";
		else
			echo "${folder}${file} - Calculation incomplete";
		fi;
	done;
	cd ..;
done
