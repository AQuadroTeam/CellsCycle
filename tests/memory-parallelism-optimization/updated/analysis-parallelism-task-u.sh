echo 1 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 1 >> recparallelism-taskthread-network.txt
echo 1 thread, prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 5 1 >> recparallelism-taskthread-network.txt
echo 2 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 2 >> recparallelism-taskthread-network.txt
echo 2 thread prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 5 2 >> recparallelism-taskthread-network.txt
echo 3 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 3 >> recparallelism-taskthread-network.txt
echo 3 thread prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 5 3 >> recparallelism-taskthread-network.txt
echo 4 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 4 >> recparallelism-taskthread-network.txt
echo 4 thread, prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 5 4 >> recparallelism-taskthread-network.txt
echo 5 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 5 >> recparallelism-taskthread-network.txt
echo 5 thread prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 5 5 >> recparallelism-taskthread-network.txt
echo 8 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 8 >> recparallelism-taskthread-network.txt
echo 8 thread prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 5 8 >> recparallelism-taskthread-network.txt
