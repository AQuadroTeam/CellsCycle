echo ll array
echo ll array UPDATE > reclla.txt
git checkout CacheLinkedListArrays
python -m memory_profiler Cache.py 10000000 100000 10000 300 5 >> reclla-ram.txt
echo 22
python -m memory_profiler Cache.py 10000000 100000 50000 300 5 >> reclla-ram.txt
echo 21
python -m memory_profiler Cache.py 10000000 100000 100000 300 5 >> reclla-ram.txt
echo 20
python -m memory_profiler Cache.py 100000 10000 10000 300 5 >> reclla-ram.txt
echo 19
python -m memory_profiler Cache.py 100000 10000 50000 300 5 >> reclla-ram.txt
echo 18
python -m memory_profiler Cache.py 100000 10000 100000 300 5 >> reclla-ram.txt
echo 17
python -m memory_profiler Cache.py 100000 10000 500000 300 5 >> reclla-ram.txt
echo 16
python -m memory_profiler Cache.py 1000000 10000 10000 900 5 >> reclla-ram.txt
echo 15
python -m memory_profiler Cache.py 1000000 10000 50000 900 5 >> reclla-ram.txt
echo 14
python -m memory_profiler Cache.py 1000000 10000 100000 900 5 >> reclla-ram.txt
echo 13
python -m memory_profiler Cache.py 1000000 10000 500000 900 5 >> reclla-ram.txt
echo 12
python -m memory_profiler Cache.py 10000000 10000 10000 900 5 >> reclla-ram.txt
echo 11
python -m memory_profiler Cache.py 10000000 10000 50000 900 5 >> reclla-ram.txt
echo 10
python -m memory_profiler Cache.py 10000000 10000 100000 900 5 >> reclla-ram.txt
echo 9
python -m memory_profiler Cache.py 10000000 10000 500000 900 5 >> reclla-ram.txt
echo 8
python -m memory_profiler Cache.py 10000000 100000 10000 300 1 >> reclla-ram.txt
echo 7
python -m memory_profiler Cache.py 10000000 100000 50000 300 1 >> reclla-ram.txt
echo 6
python -m memory_profiler Cache.py 10000000 100000 100000 300 1 >> reclla-ram.txt
echo 5
python -m memory_profiler Cache.py 10000000 100000 500000 300 1 >> reclla-ram.txt
echo 4
python -m memory_profiler Cache.py 1000000000 1000000 10000 300 5 >> reclla-ram.txt
echo 3
python -m memory_profiler Cache.py 1000000000 1000000 50000 300 5 >> reclla-ram.txt
echo 2
python -m memory_profiler Cache.py 1000000000 1000000 100000 300 5 >> reclla-ram.txt
echo 1
python -m memory_profiler Cache.py 1000000000 1000000 500000 300 5 >> reclla-ram.txt
echo finitiiiiiiiiiiiiiiiiiiii

