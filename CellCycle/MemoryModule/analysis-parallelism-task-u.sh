echo 1 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 30 1 > recparallelism-taskthread-network.txt
echo 1 thread, prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 30 1 >> recparallelism-taskthread-network.txt
echo 2 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 30 2 >> recparallelism-taskthread-network.txt
echo 2 thread prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 30 2 >> recparallelism-taskthread-network.txt
echo 3 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 30 3 >> recparallelism-taskthread-network.txt
echo 3 thread prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 30 3 >> recparallelism-taskthread-network.txt
echo 4 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 30 4 >> recparallelism-taskthread-network.txt
echo 4 thread, prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 30 4 >> recparallelism-taskthread-network.txt
echo 5 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 30 5 >> recparallelism-taskthread-network.txt
echo 5 thread prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 30 5 >> recparallelism-taskthread-network.txt
echo 8 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 30 8 >> recparallelism-taskthread-network.txt
echo 8 thread prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 30 8 >> recparallelism-taskthread-network.txt
