# -*- coding: utf-8 -*- 
from point import Point
from sage.rings.integer_ring import ZZ
from copy import copy

def vdf_eval(c, setup, Q, verbose, method):
    '''
    INPUT:
    * c the initial elliptic curve
    * setup the setup from vdf_setup function
    * Q the second point of the protocol
    * verbose
    * method for the method of storing the isogeny (kernel4, kernel4k or withoutKernel)
    OUTPUT:
    * hat_phiQ the image of Q by the dual walk
    '''
    [P, c_prime, curvesPath, kernelsOfBigSteps, phiP] = setup
    if c.Delta % (c.n-2) != 0 :
        raise RuntimeError('Delta is not a multiple of n-2')
    k = ZZ((c.n-2)//2)
    T = Q
    c_t = copy(c_prime)
    
    if method == 'kernel4k' :
        for R in kernelsOfBigSteps :
            R = R.change_iso_curve(c_t.a)
            [T, kernelPoint, listOfCurves] = R.isogeny_degree4k_strategy(T, k, method='withoutKernel', stop=1)
            c_t = T.curve
    elif method == 'kernel4' :
	cpt = 0
        for c1 in curvesPath :
            R = Point(1,1,c1).change_iso_curve(c_t.a)
            [T] = R.isogeny_degree4([T])
            c_t = T.curve
	    cpt += 1
    return T.change_iso_curve(c.a)
