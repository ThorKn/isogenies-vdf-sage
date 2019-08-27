#-*- coding: utf-8 -*-
import time
from sage.all import *

# We implement the optimal strategy when computing the isogeny walk
# Current status:
#  * OK for toy sage implem
#  * nOK for our code implem (not even tried)

from collections import deque

n = 12
m = 13
p = 2**n * 3**m - 1
Fp = GF(p)
Fpx = Fp['x']
x = Fpx.gen()
Fp2 = Fp.extension(x**2+1, 'u')
u = Fp2.gen()
E = EllipticCurve(Fp2, [3151909130, 4925574689])
assert E.is_supersingular()

# naive strategy
def naive_strat(E, S, list_of_points) :
    curve = E
    list1 = copy(list_of_points)
    R = S
    while R!=0 :
        Q = R
        while Q.order() != 4 :
            Q = 4 * Q
        phi = curve.isogeny(Q)
        R = phi(R)
        for j in range(len(list1)) :
            list1[j] = phi(list1[j])
        Q = R
        curve = phi.codomain()
    return [curve, list1]

# recursive strategy
# we do not use it, we use the iterative one
def recur_strat(E, S, list_of_points, strat) :
    if len(strat) == 0 :
        phi = E.isogeny(S)
        images = []
        for point in list_of_points :
            images.append(phi(point))
        return [phi.codomain(), images] #[phi(point) for point in list_of_points]]
    else :
        nn = strat[0]
        L = strat[1 : len(strat) + 1 - nn]
        R = strat[len(strat) + 1 - nn : len(strat)]
        T = (4**nn) * S
        [E, list1] = recur_strat(E, T, [S] + list_of_points, L)
        U = list1[0]
        [E, list2] = recur_strat(E, U, list1[1:], R)
        return [E, list2]

# optimal iterative strategy
def iter_strat(e2, E, S, list_of_points, strat) :
    QQ = deque()
    QQ.append([e2//2, S])
    i = 0
    F = E
    list1 = copy(list_of_points)
    while len(QQ) != 0 :
        [h, P] = QQ.pop()
        if h == 1 :
            phi = F.isogeny(P)
            F = phi.codomain()
            Qprime = deque()
            while len(QQ) != 0 :
                [h, P] = QQ.popleft()
                P = phi(P)
                Qprime.append([h-1, P])
            QQ = Qprime
            for j in range(len(list1)) :
                list1[j] = phi(list1[j])
        elif strat[i] > 0 and strat[i] < h :
            QQ.append([h, P])
            P = 4**(strat[i]) * P
            QQ.append([h-strat[i], P])
            i += 1
        else :
            return false
    return [F, list1]

# TEST OF CONVERSION BETWEEN WEIERSTRASS AND MONTGOMERY
def montgomery(P, alpha, s) :
    '''
    INPUT:
        * the point on the weierstrass model
        * alpha for the conversion (wiki)
        * s for the conversion (wiki)
    OUTPUT:
        * the point on the montgomery model
    '''
    x = P[0]/P[2]
    return [s*(x-alpha), 1]

import curve
alpha = E.division_polynomial(2).roots()[0][0]
s = 1/sqrt(Fp(3*alpha**2 + E.a4()))
c = curve.Curve(3**m, n, 1, Integers()(3*alpha*s), 1, 0)
# change Delta for vdf use

a = E.a4()
b = E.a6()
A = c.a
B = s

P = E.random_point()
P43 = (4**3) * P
xP43 = c.Fp2(P43[0].polynomial().list())

import point
Pmong = point.Point(montgomery(P, alpha, s)[0], 1, c)
P43mong = (4**3)*Pmong
P43mongx = c.Fp2((P43mong.x).polynomial().list())
assert P43mong.weierstrass()[0]/B == xP43

# TEST OF VALIDITY OF isogeny_degree4 AND isogeny_degree4k
# très galère de gérer les corps finis...
def changeIsomorphicCurve(P, E2) :
    from sage.schemes.elliptic_curves.weierstrass_morphism import WeierstrassIsomorphism
    C1 = P.curve()
    a1,b1 = C1.a4(), C1.a6()
    Fp2 = C1.base_ring()
    C2 = EllipticCurve(Fp2, [Fp2(E2.a4().polynomial().list()), Fp2(E2.a6().polynomial().list())])
    iso = WeierstrassIsomorphism(E=C1, F=C2)
    return iso(P)

P = E(2691078013*u + 5411211369, 5875184984*u + 3991903998)
Pmong = point.Point(montgomery(P, alpha, s)[0], 1, c)

# TEST FOR isogeny_degree4
S4 = E(5212767203*u + 1541898534, 1982433626*u + 2069840204)
S4mong = point.Point(montgomery(S4, alpha, s)[0], 1, c)
ListImage = S4mong.isogeny_degree4([Pmong])
ImagePmong = ListImage[0]
print changeIsomorphicCurve(ImagePmong.weierstrass(), E.isogeny_codomain(S4))
print E.isogeny(S4)(P)

# TEST FOR isogeny_degree4k
S = E(2527535319*u + 1865797195, 5803316480*u + 321180210)
Smong = point.Point(montgomery(S, alpha, s)[0], 1, c)
[phiPmong, phiP4kmong, listofcurves] = Smong.isogeny_degree4k(Pmong, 4, 'kernel4')
print E.isogeny(S)(P)
print changeIsomorphicCurve(phiPmong.weierstrass(), E.isogeny_codomain(S))

