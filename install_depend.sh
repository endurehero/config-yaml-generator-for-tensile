#!/bin/bash

DEPEND_DIR="./dependences"
GFLAGS_DIR="${DEPEND_DIR}/gflags"
XLRD_DIR="${DEPEND_DIR}/xlrd"

if [ ! -d ${DEPEND_DIR}]; then
    echo "the dependences dir is not exist!"
    exit 1
fi


if [ ! -d ${GFLAGS_DIR}]; then
    echo "the gflags dir is not exist!"
    exit 1
fi

if [ ! -d ${XLRD_DIR}]; then
    echo "the xlrd dir is not exist!"
    exit 1
fi


#install gflags
cd ${GFLAGS_DIR}
echo "install glags"
python setup.py install

cd ../../

#install xlrd
cd ${XLRD_DIR}
echo "install xlrd"
python setup.py install


echo "dependences install completed!"
