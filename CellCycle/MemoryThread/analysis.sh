echo master
echo master UPDATE >> recst.txt
git checkout master
python -m cProfile Cache.py 10000000 100000 100000 300 5 >> recst.txt
python -m cProfile Cache.py 10000000 100000 500000 300 5 >> recst.txt
python -m cProfile Cache.py 10000000 100000 1000000 300 5 >> recst.txt
python -m cProfile Cache.py 100000 10000 100000 300 5 >> recst.txt
python -m cProfile Cache.py 100000 10000 500000 300 5 >> recst.txt
python -m cProfile Cache.py 100000 10000 1000000 300 5 >> recst.txt
python -m cProfile Cache.py 100000 10000 5000000 300 5 >> recst.txt
python -m cProfile Cache.py 1000000 10000 100000 900 5 >> recst.txt
python -m cProfile Cache.py 1000000 10000 500000 900 5 >> recst.txt
python -m cProfile Cache.py 1000000 10000 1000000 900 5 >> recst.txt
python -m cProfile Cache.py 1000000 10000 5000000 900 5 >> recst.txt
python -m cProfile Cache.py 10000000 10000 100000 900 5 >> recst.txt
python -m cProfile Cache.py 10000000 10000 500000 900 5 >> recst.txt
python -m cProfile Cache.py 10000000 10000 1000000 900 5 >> recst.txt
python -m cProfile Cache.py 10000000 10000 5000000 900 5 >> recst.txt
python -m cProfile Cache.py 10000000 100000 100000 300 1 >> recst.txt
python -m cProfile Cache.py 10000000 100000 500000 300 1 >> recst.txt
python -m cProfile Cache.py 10000000 100000 1000000 300 1 >> recst.txt
python -m cProfile Cache.py 10000000 100000 5000000 300 1 >> recst.txt
python -m cProfile Cache.py 1000000000 1000000 100000 300 5 >> recst.txt
python -m cProfile Cache.py 1000000000 1000000 500000 300 5 >> recst.txt
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 >> recst.txt
python -m cProfile Cache.py 1000000000 1000000 5000000 300 5 >> recst.txt
echo ll array
echo ll array UPDATE >> reclla.txt
git checkout CacheLinkedListArrays
python -m cProfile Cache.py 10000000 100000 100000 300 5 >> reclla.txt
python -m cProfile Cache.py 10000000 100000 500000 300 5 >> reclla.txt
python -m cProfile Cache.py 10000000 100000 1000000 300 5 >> reclla.txt
python -m cProfile Cache.py 100000 10000 100000 300 5 >> reclla.txt
python -m cProfile Cache.py 100000 10000 500000 300 5 >> reclla.txt
python -m cProfile Cache.py 100000 10000 1000000 300 5 >> reclla.txt
python -m cProfile Cache.py 100000 10000 5000000 300 5 >> reclla.txt
python -m cProfile Cache.py 1000000 10000 100000 900 5 >> reclla.txt
python -m cProfile Cache.py 1000000 10000 500000 900 5 >> reclla.txt
python -m cProfile Cache.py 1000000 10000 1000000 900 5 >> reclla.txt
python -m cProfile Cache.py 1000000 10000 5000000 900 5 >> reclla.txt
python -m cProfile Cache.py 10000000 10000 100000 900 5 >> reclla.txt
python -m cProfile Cache.py 10000000 10000 500000 900 5 >> reclla.txt
python -m cProfile Cache.py 10000000 10000 1000000 900 5 >> reclla.txt
python -m cProfile Cache.py 10000000 10000 5000000 900 5 >> reclla.txt
python -m cProfile Cache.py 10000000 100000 100000 300 1 >> reclla.txt
python -m cProfile Cache.py 10000000 100000 500000 300 1 >> reclla.txt
python -m cProfile Cache.py 10000000 100000 1000000 300 1 >> reclla.txt
python -m cProfile Cache.py 10000000 100000 5000000 300 1 >> reclla.txt
python -m cProfile Cache.py 1000000000 1000000 100000 300 5 >> reclla.txt
python -m cProfile Cache.py 1000000000 1000000 500000 300 5 >> reclla.txt
python -m cProfile Cache.py 1000000000 1000000 1000000 300 5 >> reclla.txt
python -m cProfile Cache.py 1000000000 1000000 5000000 300 5 >> reclla.txt
poweroff
