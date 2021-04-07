import pytest
import pandas as pd
import numpy as np

from ip_to_ip import createCSR
# from ip_to_ip import ip_to_ip
# from ip_to_ip import applyPrune


def test_createCSR():
    data = [[0,1], [0,2], [0,2], [2,0], [2,0], [2,0]]
    df_test = pd.DataFrame(data,columns=['srcint','destint'])
    answer = [[0, 1, 2],[0,0,0], [3,0,0]]
    
    testData = createCSR(df_test)
    testData_asArray = testData.toarray()

    assert np.array_equal(answer, testData_asArray)
