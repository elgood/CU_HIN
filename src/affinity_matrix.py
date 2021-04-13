from scipy.sparse import lil_matrix, csr_matrix
import numpy as np
import math


def affinity_matrix(M: csr_matrix, threshold: float) -> csr_matrix:
  """ Computes the affinity matrix for matrix M.  Each row is compared to each other row
    and a gaussian is used to calculate how close the rows are.  If the value is below a 
    threshold, we set it to zero (which won't be represented in the sparse matrix)

  Arguments:
  M: csr - The matrix to compute affinity on.
  threshold: float - The threshold to use to zero out small values

  Returns:
  csr_matrix

  """

  assert(M.shape[0] == M.shape[1]),("Expected square matrix")
  assert(len(M.shape) == 2),("Expected square matrix")
  n = M.shape[0]

  A = lil_matrix((n,n))

  for i in range(n):
    for j in range(n):
      if i != j:
        x = M[i,:].toarray() - M[j,:].toarray()
        x = np.linalg.norm(x, ord=2)
        y = math.exp(-pow(x,2))
        if y > threshold:
          A[i,j] = y

  return A.tocsr()


  


