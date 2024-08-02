This repo contains the source code and evaluation of the work titled "Differentially-private version of a Bloom filter".

The implementation is in Python 2.7.

The list of code files.
- /pics: contains an Evaluation charts
- evalsParallel2.py: contains a list of experiments
- result.txt: is the logging of experiments
- textProcessing.py: is a library for string management
- ultrafilter.py: is the main source code for differentially private bloom filter.


## How to run
+ Setup environment
```
virtualenv -p /usr/bin/python py2env
source py2env/bin/activate
pip install -r requirements.txt
```
+ Executing from command line
```
python ultrafilter.py
```

+ Running evaluation
```
python evalsParallel2.py
```
