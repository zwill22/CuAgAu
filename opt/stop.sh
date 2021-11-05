#!/bin/bash

i=${1}

while [ ${i} -le ${2} ]; do
    scancel ${i}
    let i=i+1
done
