echo master
echo master > recparallelism-single.txt
git checkout master
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 >> recparallelism-single.txt
echo -1
python -m cProfile Cache.py 100000 10000 5000000 300 5 >> recparallelism-single.txt
echo parallelism
echo parallelism > recparallelism-multi.txt
git checkout MemoryParallelism
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 >> recparallelism-multi.txt
echo -1
python -m cProfile Cache.py 100000 10000 5000000 300 5 >> recparallelism-multi.txt
echo finito

