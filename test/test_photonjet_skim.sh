#!/bin/bash
source /cvmfs/sft.cern.ch/lcg/views/LCG_107a/x86_64-el9-gcc14-opt/setup.sh

python3 src/main.py skim \
  --filepath data/DT_2024/EGamma/Run2024H.txt \
  --golden_json /eos/user/c/cmsdqm/www/CAF/certification/Collisions24/2024H_Golden.json \
  --triggerpath data/triggerlists/EGM_triggers_skim.txt \
  --out out_skim \
  --channel photonjet \
  --nThreads 8 \
  --nsteps 10 \
  --step 1 \
  --correction_json data/corrections/summer24_corrections.json \
  --correction_key Run2024H \
  --progress_bar

RET=$?

if [ $RET -ne 0 ]; then
  exit $RET
fi

python3 src/main.py hist \
  -hconf data/histograms/EGM_histograms.ini \
  -fl out_skim/J4PSkim_photonjet_1.root \
  --triggerpath data/triggerlists/EGM_triggers.txt \
  -loc \
  -pbar \
  --nThreads 8 \
  --out out_hist \
  --run_tag photonjet

RET=$?

exit $RET