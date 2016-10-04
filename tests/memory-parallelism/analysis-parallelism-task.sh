echo task > recparallelism-taskthread.txt
echo 1 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 1 >> recparallelism-taskthread.txt
echo 1 thread, prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 5 1 >> recparallelism-taskthread.txt
echo 2 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 2 >> recparallelism-taskthread.txt
echo 2 thread prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 5 2 >> recparallelism-taskthread.txt
echo 3 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 3 >> recparallelism-taskthread.txt
echo 3 thread prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 5 3 >> recparallelism-taskthread.txt
echo finito
