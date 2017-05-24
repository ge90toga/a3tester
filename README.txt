This is a self-written testing script for testing UNSW COMP9319 assignment3.

- The idea of this test is the test script going through all file and read every word,
stem the word by calling calling a C stemming program. And if the word matches one of the searching term, record its frequency.

- After finishing the slow word by word search, it will call your c/c++ program, do a 100% string comparison against its own.

- it also saves your result `cpp.out.txt` and its own result `script.out.txt` for reference.

### HOW TO USE
(1) create a directory called `a3tester` in your assignment directory and clone the project into that directory. The structure would be like:
```
YOUR-ASSIGNMENT-DIR
    - <your-test-dir>
    - <your-index-dir>
    - a3search.cpp
    - a3tester
      - a3tester.py
      - stemlib
```

(2) compile the stemming library the testing script is going to use by going to `stemlib` and do `make`

(3) To conduct test, run the following command `python3 a3tester.py <testfilePath> <indexPath> "term1" "term2"`.

Please DONT'T add './' for your index and text directory. If your have the above folder structure and say your
<your-test-dir> is "testfiles", your index directory is "index". Run following:
```
python3 a3tester.py testfiles/booknmail index "david" "tim"
python3 a3tester.py testfiles/books200m index1 "apple" "banana" "rock"
python3 a3tester.py testfiles/simple index2 "Apple" "iNvestor"
```

### NOTE:

This test does not guarantee any correctness whatsoever, use it as your your discretion.