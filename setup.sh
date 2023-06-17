#!/bin/bash

name="BlendArMocap"

branch=$(git symbolic-ref --short HEAD)
version_str=$(grep -r '"version":' __init__.py | tr -d '[a-z,_."(): ]')

prefix=("_"$branch"_"$version_str)
dirpath=$(pwd)

zipcmd() {
    zip -r $name/$name$prefix.zip $name \
    -x "__MAXOSX/*" -x "*.DS_Store" \
    -x "*venv*" -x "*.idea*" -x "*.git*" \
    -x "*__pycache__*" -x "*docs*" -x "*setup*" \
    -x "*swp", -x "*test*"
}

cd ..
zipcmd
cd $name
