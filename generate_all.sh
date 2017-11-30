#!/bin/bash


export NOW=$(date +%Y%m%d%H%M%S)
export THIS=$(basename $0)
export RUNAS=$(whoami)
export WHEREAMI=$(dirname $0)

SUBDIR="${1}"
WEEKS=6

if [ -z "${2}" ]
then
	echo "creating default 6 week program"
else
	WEEKS=${2}
	echo "creating ${WEEKS} week program"
fi

if [ -z "${SUBDIR}" ]
then
	echo "subdir not provided" && exit 99
fi

if [ -d "${SUBDIR}" ]
then
	echo "found subdir ${SUBDIR}"
else
	echo "could not find subdir ${SUBDIR}"
fi

echo "#${SUBDIR^}" > ${WHEREAMI}/${SUBDIR}/README.md
echo >> ${WHEREAMI}/${SUBDIR}/README.md

for YAML in $(ls ${WHEREAMI}/${SUBDIR}/*.yaml)
do

	filename=$(basename $YAML)
	extension="${filename##*.}"
	filename="${filename%.*}"
	
	echo $filename
	

	
	python ${WHEREAMI}/inol.py --output ${WHEREAMI}/${SUBDIR}/${filename} --weeks ${WEEKS}  --config ${WHEREAMI}/${SUBDIR}/${filename}.yaml
	
	if [ -f ${WHEREAMI}/${SUBDIR}/${filename}/README.md ]
	then
		cat ${WHEREAMI}/${SUBDIR}/${filename}/README.md >> ${WHEREAMI}/${SUBDIR}/README.md
	fi
done


