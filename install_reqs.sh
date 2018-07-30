#!/usr/bin/env bash

INSTALL_DIR="/usr/local/bin/"
if [[ $1 == "-g" ]]
then
	INSTALL_DIR="/usr/bin/pip"
fi

piplist=$(ls $INSTALL_DIR | grep "pip")
PIP_TOOL="pip"
for i in $piplist
do
	PIP_TOOL="$i"
done

$PIP_TOOL install requests
$PIP_TOOL install urllib3
