#!/bin/bash


export NOW=$(date +%Y%m%d%H%M%S)
export THIS=$(basename $0)
export RUNAS=$(whoami)
export WHEREAMI=$(dirname $0)


for YAML in $(ls ${WHEREAMI}/*.yaml)
do

	filename=$(basename $YAML)
	extension="${filename##*.}"
	filename="${filename%.*}"
	
	echo $filename
	
	#if [ -d ${WHEREAMI}/${filename} ]
	#then
	#	mv ${WHEREAMI}/${filename} ${WHEREAMI}/${filename}.${NOW}
	#fi
	
	python ${WHEREAMI}/inol.py --output ${WHEREAMI}/${filename} --weeks 6  --config ${WHEREAMI}/${filename}.yaml
	#python ${WHEREAMI}/inol.py --verbose --output ${WHEREAMI}/${filename} --weeks 6  --config ${WHEREAMI}/${filename}.yaml
	
done