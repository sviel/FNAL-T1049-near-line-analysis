RUN=${1}

if [ ! ${RUN} ]
then
    echo "Usage: source run_decoder_correlated.sh runNumber"
    return
fi

DAT="./data/May20/vmm000"${RUN}"_sample.txt"
OUT="./data/May20/vmm000"${RUN}"_decoded_sample.txt"

echo "Input data: "${DAT}
echo "Output: "${OUT}
    
if [ -f ${DAT} ]
then
    root -l -b -q 'decoder_correlated.C+("'${DAT}'")' | grep -v "Processing" | grep -v "class" | grep -v "Warning" > ${OUT}
else
    echo "Input data not found!"
fi

