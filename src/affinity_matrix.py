from scipy.sparse import lil_matrix, csr_matrix, dia_matrix
import numpy as np
import math
import logging


def affinity_matrix(M: csr_matrix, threshold: float) -> csr_matrix:
  """ Computes the affinity matrix for matrix M.  Each row is compared to each 
    other row and a gaussian is used to calculate how close the rows are.  
    If the value is below a threshold, we set it to zero (which won't 
    be represented in the sparse matrix)

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
    mi = M[i,:].toarray()
    for j in range(i):
      if i != j:
        x = mi - M[j,:].toarray()
        x = np.linalg.norm(x, ord=2)
        y = math.exp(-pow(x,2))
        if y > threshold:
          A[i,j] = y
          A[j,i] = y

  return A.tocsr()


def converge(M, Y, mu, tol):

  assert(M.shape[0] == M.shape[1]),("Expected square matrix")
  assert(len(M.shape) == 2),("Expected square matrix")
  n = M.shape[0]
  
  data = np.squeeze(np.asarray(M.sum(axis=1))) # sum the rows
  offsets = np.array([0])
  D = dia_matrix((data, offsets), shape=(n,n))  

  D = D.tocsr() # Convert to csr because can't use subscripting
  for i in range(n):
    D[i,i] = D[i,i] ** (-1/2)

  S = D * M * D

  alpha = 1/(1 + mu)
  beta = mu/(1 + mu)

  delta=tol+1 #Initializes change as larger than the tolerance to enter while loop.
  F = Y

  while delta>tol:
    F0=F #Stores previous value of F for computation.
    F = alpha * S.dot(F) + beta * Y
    delta=np.linalg.norm(F-F0) #Computes magnitude of change from previous step.
    logging.info("Tol " + str(tol) + " Delta " + str(delta)) 
  
  return F
