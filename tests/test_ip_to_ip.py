import pytest
import pandas as pd
import numpy as np

from src.ip_to_ip import createCSR
# from ip_to_ip import ip_to_ip
# from ip_to_ip import applyPrune


def test_createCSR():
    # Setup
    data = [[0,1],[0,2],[0,2],[2,0],[2,0],[2,0]]                # integer pairs of IP's
    df_test = pd.DataFrame(data,columns=['srcint','destint'])   # pandas dataframe...
    answer = [[0,1,2],[0,0,0],[3,0,0]]                          # dense matrix
    
    # Test 
    testData = createCSR(df_test)
    testData_asArray = testData.toarray()

    assert np.array_equal(answer, testData_asArray)
