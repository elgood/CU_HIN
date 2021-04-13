import numpy as np
import scipy.sparse as sparse
import scipy.stats as stats
import pandas as pd
import logging

#See Preliminary Results for more detailed explanation on what each part does.

def PathSim(M):
    '''Computes PathSim for individual metapath M.
    Output: Partial similarity matrix Mp (csr_matrix).'''

    n = M.shape[0]
    assert(M.shape[0], M.shape[1]),("Must be square")
    assert(len(M.shape) == 2),("Must be square")

    # Create a lil matrix because they are cheap to build incrementally.
    Mp=sparse.lil_matrix((n,n)) 
    rows, cols = M.nonzero()

    tuples = zip(*sorted(zip(rows, cols)))
    rows, cols = [ list(tuple) for tuple in tuples ]
    logging.info("Number of items to perform pathsim: " + str(len(rows)))
    for index in range(len(rows)):
      i = rows[index]
      j = cols[index]
      Mp[i,j] = 2 * (float(M[i,j]) / (M[i,i] + M[j,j]))

    return Mp.tocsr()
         
    '''
    Mp=sparse.csr_matrix((n,n)) #Creates empty csr matrix.
    w=LaplacianWeight(M,n) #Calls Laplacian weight function.
    for j in range(n):
        mj=M[j,j] #Will be accessed n times in each iteration of outer loop.
        for i in range(n):
        #In j,i order to take advantage of row format.
        #There is probably a more efficent way to loop through a csr matrix than a double for loop. I will look into this later.
            Mp[i,j]=2*w*M[i,j]/(M[i,i]+mj) #Computes unweighted PathSim.
    '''
    return Mp

def LaplacianWeight(M,n,t=1):
    '''Computes Laplacian weight for individual metapath M.
    Inputs: Metapath M (csr_matrix), size of matrix n (int), connection scaling t (positive real, default 1).
    Output: Laplacian weight w (float).'''
    #Under development, will complete later. Set to 1/6 as a default.
    w=1/6
    return w

def TransductiveClassifier(Mp,n,Y,mu=1,tol=0.0001):
    '''Transductive classifier for similarity matrix Mp.
    Inputs: Similarity matrix M (csr_matrix), size of matrix n (int), label matrix Y (np.array),
    fitting constant mu (positive real, default 1), tolerance (positive real, default 10e-4).
    Output: Partial similarity matrix Mp (np.array).'''

    a=1/(1+mu) #Alpha value.
    b=mu*a #Beta value.
    d=Mp.sum(axis=1)
    D=sparse.diags(d,'csr') #Creates diagonal matrix containing
    S=D**(-1/2)@Mp@D**(1/2) #Computes S matrix for iterating.
    F=Y #Initializes the classifier to the known labels.
    delta=tol+1 #Initializes change as larger than the tolerance to enter while loop.
    while delta>tol:
        F0=F #Stores previous value of F for computation.
        F=a*S@F+b*Y #Iterative step.
        delta=np.linalg.norm(F-F0) #Computes magnitude of change from previous step.
    return F
    #Untested, will finalize this week.

def get_HIN_matrix():
    ''' Under development, will eventually read files and output one of the 6 HIN matrices.
    Currently generates a random matrix.'''
    n=10
    M=sparse.random(n,n,density=.25,format='csr')
    M=M+M.T+sparse.eye(n,format='csr')
    for j in range(n):
        for i in range(n):
            if M[i,j]!=0:
                M[i,j]=1
    return M

def get_Y():
    n=10
    Y=np.zeros(shape=(n,2))
    for i in range(n):
        r=np.random.uniform()
        print(r)
        Y[i,0]=r
        Y[i,1]=1-r
    return Y
    #Under development, currently generates random matrix.

def main():
    n=10
    Q=get_HIN_matrix()
    N=get_HIN_matrix()
    R=get_HIN_matrix()
    S=get_HIN_matrix()
    C=get_HIN_matrix()
    D=get_HIN_matrix() #Randomly generates HIN matrices.
    Mp=PathSim(Q,n)+PathSim(C,n)+PathSim(Q@Q.T,n)+PathSim(R@R.T,n)+PathSim(Q@N@Q.T,n)+PathSim(R@D@R.T,n)
    #Computes full similarity matrix.
    Y=get_Y()
    print(Y)

if __name__ == '__main__':
    main()
