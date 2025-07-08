This is an project on learning a frequency counting of event at scale. We have adapted core ideas in the [paper](https://docs-assets.developer.apple.com/ml-research/papers/learning-with-privacy-at-scale.pdf).

The implementation is in Python.

The list of code files.
- aclient.py : This is the client side code for gathering data on the user end before transmitting to the server.

- aserver.py: This is the server side code that processes the request from the clients.

- contract.py: This is an interface that we use to simulate an interaction between server and client. We did not create a REST API due to time constraint.

- helper.py: This is the supporting code that are shared across client and server.

- textProcessing.py: This is used for managing textual input.

- evals.py: This has a list of experiments.

## How to run
+ Setup environment
```
virtualenv -p /usr/bin/python py2env
source py2env/bin/activate
pip install -r requirements.txt
```
+ Executing from command line
```
python contract.py
```

