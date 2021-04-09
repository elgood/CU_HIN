# Unit tests go here.

### Setting up PYTHONPATH

Make sure that the CU_HIN/src directory is in your PYTHON PATH.

If using virtualenv, add the following to your activate file:
```
export PYTHONPATH=<CU_HIN absolute path>/src
```

otherwise:

```
export PYTHONPATH=${PYTHONPATH}:<CU_HIN absolute path>/src
```


### Running Tests

```
pytest
```