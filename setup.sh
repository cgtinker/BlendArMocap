#!/bin/bash

name="BlendArMocap"
version="_release_160"
dirpath=$(pwd)

zipcmd() {
    zip -r $name/$name$version.zip $name \
    -x "__MAXOSX/*" -x "*.DS_Store" \
    -x "*venv*" -x "*.idea*" -x "*.git*" \
    -x "*__pycache__*" -x "*docs*" -x "*setup*" \
    -x "*swp", -x "*test*"
}

cd ..
zipcmd
cd $name
