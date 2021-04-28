import numpy as np
import scipy.sparse as sparse
import scipy.stats as stats
import pandas as pd
import logging
import time #For testing, will probably remove.

#See Preliminary Results for more detailed explanation on what each part does.

def PathSim(M):
    '''Computes PathSim for individual metapath M.
    Output: Partial similarity matrix Mp (csr_matrix).'''

    n = M.shape[0]
    assert(M.shape[0], M.shape[1]),("Must be square")
    assert(len(M.shape) == 2),("Must be square")

    w=LaplacianWeight(M,n)
    # Create a lil matrix because they are cheap to build incrementally.
    Mp=sparse.lil_matrix((n,n)) 
    rows, cols = M.nonzero()

    tuples = zip(*sorted(zip(rows, cols)))
    rows, cols = [ list(tuple) for tuple in tuples ]
    logging.info("Number of items to perform pathsim: " + str(len(rows)))
    for index in range(len(rows)):
      i = rows[index]
      j = cols[index]
      Mp[i,j] = 2 * w * (float(M[i,j]) / (M[i,i] + M[j,j]))

    return Mp.tocsr()

def LaplacianWeight(M,n,t=1):
    '''Computes Laplacian weight for individual metapath M.
    Inputs: Metapath M (csr_matrix), size of matrix n (int), connection scaling t (positive real, default 1).
    Output: Laplacian weight w (float).'''
    #Under development, will complete later. Set to 1/6 as a default.
    w=1/6
    return w

def TransductiveClassifier(Mp,Y,mu=1,tol=0.0001):
    '''Transductive classifier for similarity matrix Mp.
    Inputs: Similarity matrix M (csr_matrix), size of matrix n (int), label matrix Y (np.array),
    fitting constant mu (positive real, default 1), tolerance (positive real, default 10e-4).
    Output: Partial similarity matrix Mp (np.array).'''

    a=1/(1+mu) #Alpha value.
    b=mu*a #Beta value.
    d=np.squeeze(np.asarray(Mp.sum(axis=1))) #Row sums of Mp.
    S=sparse.diags(d**(-1/2),format='csr')@Mp@sparse.diags(d**(1/2),format='csr') #Computes S matrix for iterating.
    F=Y #Initializes the classifier to the known labels.
    delta=tol+1 #Initializes change as larger than the tolerance to enter while loop.
    while delta>tol:
        F0=F #Stores previous value of F for computation.
        F=a*S@F+b*Y #Iterative step.
        delta=np.linalg.norm(F-F0) #Computes magnitude of change from previous step.

    return F
    #Works, but does not converge, possibly due to random matrices being generated instead of more realistic ones.
    #Under further investigation; increasing the size and decreasing the density does not help.
    #I will work out the mathematical conditions for convergence and update them so the random matrices converge.

def get_HIN_matrix():
    ''' Under development, will eventually read files and output one of the 6 HIN matrices.
    Currently generates a random matrix.'''
    n=100
    M=sparse.random(n,n,density=.01,format='csr')
    M=M+M.T+sparse.eye(n,format='csr')
    for j in range(n):
        for i in range(n):
            if M[i,j]!=0:
                M[i,j]=1
    return M

def get_Y():
    n=100
    Y=np.zeros(shape=(n,2))
    for i in range(n):
        r=np.random.uniform()
        Y[i,0]=r
        Y[i,1]=1-r
    return Y
    #Under development, currently generates random symmetric matrix.

def main():
    n=100
    Q=get_HIN_matrix()
    N=get_HIN_matrix()
    R=get_HIN_matrix()
    S=get_HIN_matrix()
    C=get_HIN_matrix()
    D=get_HIN_matrix() #Randomly generates HIN matrices for now.
    Mp=PathSim(Q)+PathSim(C)+PathSim(Q@Q.T)+PathSim(R@R.T)+PathSim(Q@N@Q.T)+PathSim(R@D@R.T)
    #Computes full similarity matrix.
    print(Mp.todense())
    Y=get_Y()
    F=TransductiveClassifier(Mp,Y)
    print(F)

if __name__ == '__main__':
    main()
