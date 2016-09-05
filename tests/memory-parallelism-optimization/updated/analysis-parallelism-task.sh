echo task > recparallelism-taskthread-pickle.txt
git checkout MemoryParallelism-Optmization
echo 1 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 1 >> recparallelism-taskthread-pickle.txt
echo 1 thread, prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 5 1 >> recparallelism-taskthread-pickle.txt
echo 2 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 2 >> recparallelism-taskthread-pickle.txt
echo 2 thread prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 5 2 >> recparallelism-taskthread-pickle.txt
echo 3 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 3 >> recparallelism-taskthread-pickle.txt
echo 3 thread prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 5 3 >> recparallelism-taskthread-pickle.txt
echo 4 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 4 >> recparallelism-taskthread-pickle.txt
echo 4 thread, prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 5 4 >> recparallelism-taskthread-pickle.txt
echo 5 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 5 >> recparallelism-taskthread-pickle.txt
echo 5 thread prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 5 5 >> recparallelism-taskthread-pickle.txt
echo 8 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 8 >> recparallelism-taskthread-pickle.txt
echo 8 thread prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 5 8 >> recparallelism-taskthread-pickle.txt

echo Start cpickle, good luck
echo task > recparallelism-taskthread-cpickle.txt
git checkout MemoryParallelism-Optmization-cpickle
echo 1 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 1 >> recparallelism-taskthread-cpickle.txt
echo 1 thread, prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 5 1 >> recparallelism-taskthread-cpickle.txt
echo 2 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 2 >> recparallelism-taskthread-cpickle.txt
echo 2 thread prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 5 2 >> recparallelism-taskthread-cpickle.txt
echo 3 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 3 >> recparallelism-taskthread-cpickle.txt
echo 3 thread prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 5 3 >> recparallelism-taskthread-cpickle.txt
echo 4 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 4 >> recparallelism-taskthread-cpickle.txt
echo 4 thread, prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 5 4 >> recparallelism-taskthread-cpickle.txt
echo 5 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 5 >> recparallelism-taskthread-cpickle.txt
echo 5 thread prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 5 5 >> recparallelism-taskthread-cpickle.txt
echo 8 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 8 >> recparallelism-taskthread-cpickle.txt
echo 8 thread prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 5 8 >> recparallelism-taskthread-cpickle.txt

git checkout MemoryParallelism-Optmization-import
echo o > recparallelism-taskthread-cpickle2.txt
echo 1 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 1 >> recparallelism-taskthread-cpickle2.txt
echo 1 thread, prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 5 1 >> recparallelism-taskthread-cpickle2.txt
echo 2 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 2 >> recparallelism-taskthread-cpickle2.txt
echo 2 thread prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 5 2 >> recparallelism-taskthread-cpickle2.txt
echo 3 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 3 >> recparallelism-taskthread-cpickle2.txt
echo 3 thread prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 5 3 >> recparallelism-taskthread-cpickle2.txt
echo 4 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 4 >> recparallelism-taskthread-cpickle2.txt
echo 4 thread, prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 5 4 >> recparallelism-taskthread-cpickle2.txt
echo 5 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 5 >> recparallelism-taskthread-cpickle2.txt
echo 5 thread prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 5 5 >> recparallelism-taskthread-cpickle2.txt
echo 8 thread
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 8 >> recparallelism-taskthread-cpickle2.txt
echo 8 thread prova 2
python -m cProfile Cache.py 100000 10000 5000000 300 5 8 >> recparallelism-taskthread-cpickle2.txt
echo finito
cat recparallelism-taskthread-pickle.txt | grep -n -e "function calls" > recparallelism-taskthread-pickle-sintex.txt 
cat recparallelism-taskthread-cpickle.txt | grep -n -e "function calls" > recparallelism-taskthread-cpickle-sintex.txt
cat recparallelism-taskthread-cpickle2.txt | grep -n -e "function calls" > recparallelism-taskthread-cpickle2-sintex.txt
sudo poweroff
