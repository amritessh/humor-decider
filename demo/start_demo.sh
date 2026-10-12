cd /work/strands-decider
S=/work/venv-train/bin/strands-decider; P=/work/venv-train/bin/python
up() { $P -c "import urllib.request as u; u.urlopen('http://localhost:$1/health')" 2>/dev/null; }
up 8101 || nohup $S serve StrandsAgents/strands-decider-2B-hobson-v21 --port 8101 >/work/logs/s101.log 2>&1 &
up 8103 || nohup $S serve checkpoints/conan-v21b-s5 --port 8103 >/work/logs/s103.log 2>&1 &
for p in 8101 8103; do n=0; until up $p; do sleep 5; n=$((n+1)); [ $n -gt 60 ] && { echo "port $p did not come up; see /work/logs/s${p#8}.log"; exit 1; }; done; echo $p up; done
pkill -f demo.py 2>/dev/null
nohup $P /work/conan/demo.py >/work/logs/demo.log 2>&1 &
sleep 2; echo demo started; tail -n 3 /work/logs/demo.log
