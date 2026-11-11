#!/bin/bash
# renderiza todos os shots (fila compartilhada, N workers). uso: render_all.sh <workers> shots...
HERE=$(cd "$(dirname "$0")" && pwd); F=$HERE/../frames; mkdir -p $F/logs
Q=$F/queue.txt; : > $Q; for s in "${@:2}"; do echo $s >> $Q; done
worker() {
  while true; do
    s=$(flock $Q.lock -c "head -n1 $Q; sed -i '1d' $Q")
    [ -z "$s" ] && break
    $HERE/run.sh $s $F/$s full 720 1280 4 > $F/logs/$s.log 2>&1
    echo "$(date +%T) $s $(ls $F/$s/*.png 2>/dev/null | wc -l)" >> $F/logs/progress.txt
  done
}
for i in $(seq $1); do worker & sleep 2; done
wait; echo ALLDONE >> $F/logs/progress.txt
