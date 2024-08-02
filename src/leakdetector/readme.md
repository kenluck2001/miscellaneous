# Privacy Leak Estimation

This work contains the experiments that are needed to demonstrate if data sets are susceptible to privacy leaks based on the inherent structure of the data derived from information-theoretic measures.


All the code is tested in Python 2.7
- experiments.py : This contains the source code for the experiments.

### Datasets
- [machine-prediction.csv](https://www.kaggle.com/datasets/umerrtx/machine-failure-prediction-using-sensor-data)
- [customer-purchase.csv](https://www.kaggle.com/datasets/rabieelkharoua/predict-customer-purchase-behavior-dataset)
- [employee-attrition.csv](https://www.kaggle.com/datasets/mrsimple07/employee-attrition-data-prediction)


All charts were made using matplotlib.


## How to run
+ Setup environment
```
virtualenv -p /usr/bin/python py2env
source py2env/bin/activate
pip install -r requirements.txt
```

+ Running evaluation
```
python experiments.py
```
