#!/bin/bash
# round 5 CPU chains (run in the background; logs in pooling_v5_work). Chain A: padding variants for all models; chain B: rotation, white-box attack, item 5.
cd /Users/manish/Code/mtp/Agentic-Harness
P=/Users/manish/Code/mtp/nebula-venv/bin/python; L=/Users/manish/Code/mtp/pooling_v5_work
export NTHREADS=4
chainA() {
  while [ ! -f $L/pad_sur_old_done ]; do sleep 20; done
  for v in block syswow clean rare; do $P scripts/round5/r5_pad.py --variant $v --models released,A,C,ATTbal,MMbal,Cbal --seeds-old 5 --seeds-new 5 --out pad_$v > $L/padA_$v.log 2>&1; done
  for v in sur_lgb sur_c; do $P scripts/round5/r5_pad.py --variant $v --models released,A,C,ATTbal --seeds-old 5 --seeds-new 5 --out pad_$v > $L/padA_$v.log 2>&1; done
  echo ALLDONE > $L/chainA_done
}
chainB() {
  $P scripts/round5/r5_rotation.py --models released,A,C,F,ATTbal --seeds-old 5 --seeds-new 10 --seeds-f 3 --out rotation > $L/rotB.log 2>&1
  $P scripts/round5/r5_attack.py --models ATTbal,Cbal,released > $L/attack.log 2>&1
  $P scripts/round5/r5_graded.py > $L/graded.log 2>&1
  $P scripts/round5/r5_pad.py --variant random --models released,A,C,C2,ATTbal,MMbal,Cbal --seeds-old 10 --seeds-new 10 --out pad_random > $L/padB_random.log 2>&1
  echo ALLDONE > $L/chainB_done
}
chainA &
chainB &
wait
