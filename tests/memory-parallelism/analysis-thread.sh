echo parallelism
echo parallelism > recparallelism-multi.txt

echo "1 getter, 1 setter"
python -m cProfile Cache.py 1000000000 1000000 100000 300 5 1 >> recparallelism-multi.txt
echo -1
python -m cProfile Cache.py 100000 10000 500000 300 5 1 >> recparallelism-multi.txt

echo "2 getter, 1 setter"
python -m cProfile Cache.py 1000000000 1000000 100000 300 5 2 >> recparallelism-multi.txt
echo -1
python -m cProfile Cache.py 100000 10000 500000 300 5 2 >> recparallelism-multi.txt

echo "3 getter, 1 setter"
python -m cProfile Cache.py 1000000000 1000000 100000 300 5 3 >> recparallelism-multi.txt
echo -1
python -m cProfile Cache.py 100000 10000 500000 300 5 3 >> recparallelism-multi.txt

echo "4 getter, 1 setter"
python -m cProfile Cache.py 1000000000 1000000 100000 300 5 4 >> recparallelism-multi.txt
echo -1
python -m cProfile Cache.py 100000 10000 500000 300 5 4 >> recparallelism-multi.txt

echo "5 getter, 1 setter"
python -m cProfile Cache.py 1000000000 1000000 100000 300 5 5 >> recparallelism-multi.txt
echo -1
python -m cProfile Cache.py 100000 10000 500000 300 5 5 >> recparallelism-multi.txt

echo "6 getter, 1 setter"
python -m cProfile Cache.py 1000000000 1000000 100000 300 5 6 >> recparallelism-multi.txt
echo -1
python -m cProfile Cache.py 100000 10000 500000 300 5 6 >> recparallelism-multi.txt

echo "7 getter, 1 setter"
python -m cProfile Cache.py 1000000000 1000000 100000 300 5 7 >> recparallelism-multi.txt
echo -1
python -m cProfile Cache.py 100000 10000 500000 300 5 7 >> recparallelism-multi.txt

echo "10 getter, 1 setter"
python -m cProfile Cache.py 1000000000 1000000 100000 300 5 10 >> recparallelism-multi.txt
echo -1
python -m cProfile Cache.py 100000 10000 500000 300 5 10 >> recparallelism-multi.txt

echo "15 getter, 1 setter"
python -m cProfile Cache.py 1000000000 1000000 100000 300 5 15 >> recparallelism-multi.txt
echo -1
python -m cProfile Cache.py 100000 10000 500000 300 5 15 >> recparallelism-multi.txt

echo "20 getter, 1 setter"
python -m cProfile Cache.py 1000000000 1000000 100000 300 5 20 >> recparallelism-multi.txt
echo -1
python -m cProfile Cache.py 100000 10000 500000 300 5 20 >> recparallelism-multi.txt

echo "30 getter, 1 setter"
python -m cProfile Cache.py 1000000000 1000000 100000 300 5 30 >> recparallelism-multi.txt
echo -1
python -m cProfile Cache.py 100000 10000 500000 300 5 30 >> recparallelism-multi.txt
echo finito
