RUN=${1}
WHOLE=${2}

if [ ${#} -ne 2 ]
then
    echo "Usage: source run_plot_correlated.sh runNumber doWholeRun"
    return
fi

DAT="./data/May20/vmm000"${RUN}"_decoded"
OUT="./output/run_"${RUN}

echo "Input data: "${DAT}
echo "Output: "${OUT}

if [ ${WHOLE} -eq 0 ]
then
   echo "Run on small sample"
   DATFILE=${DAT}"_sample.txt"
else
   echo "Process whole run"
   DATFILE=${DAT}".txt"
fi

echo

if [ -f ${DATFILE} ]
then
    mkdir -p ${OUT}

    ## python plot_correlated.py <filename> <outdir> [doBeam doFast doWholeRun doPixel doSynch doAtone]
    python plot_correlated.py ${DAT} ${OUT} 1 0 ${WHOLE} 1 0 1
else
    echo "Input data not found!"
fi

