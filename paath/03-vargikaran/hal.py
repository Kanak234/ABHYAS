# -*- coding: utf-8 -*-
# पाठ ३ का सही हल — बच्चों वाले package में नहीं जाता.

import math


def sigmoid(z):
    # बहुत बड़ी या बहुत छोटी z पर math.exp फट जाता है (OverflowError),
    # इसलिए दोनों तरफ़ बाँध दिया. यह असली code में भी ऐसे ही किया जाता है.
    if z < -500:
        return 0.0
    if z > 500:
        return 1.0
    return 1.0 / (1.0 + math.exp(-z))


def shuddhata(asli, anuman):
    if len(asli) == 0:
        return 0.0
    sahi = 0
    for i in range(len(asli)):
        if asli[i] == anuman[i]:
            sahi += 1
    return sahi / float(len(asli))


def varg_batao(X, y, naye_X):
    n = len(X)
    vg = len(X[0])

    # पैमाना — पाठ २ वाला ही काम
    ausat = []
    vichalan = []
    for j in range(vg):
        stambh = [X[i][j] for i in range(n)]
        a = sum(stambh) / float(n)
        v = math.sqrt(sum((m - a) ** 2 for m in stambh) / n)
        ausat.append(a)
        vichalan.append(v)

    def badlo(pankti):
        out = []
        for j in range(vg):
            if vichalan[j] == 0:
                out.append(pankti[j] - ausat[j])
            else:
                out.append((pankti[j] - ausat[j]) / vichalan[j])
        return out

    Xs = [badlo(p) for p in X]

    w = [0.0] * vg
    b = 0.0
    dar = 0.1
    for _ in range(3000):
        wd = [0.0] * vg
        bd = 0.0
        for i in range(n):
            z = b
            for j in range(vg):
                z += w[j] * Xs[i][j]
            p = sigmoid(z)
            galti = y[i] - p
            for j in range(vg):
                wd[j] += Xs[i][j] * galti
            bd += galti
        for j in range(vg):
            w[j] += dar * wd[j] / n
        b += dar * bd / n

    jawab = []
    for pankti in naye_X:
        ps = badlo(pankti)
        z = b
        for j in range(vg):
            z += w[j] * ps[j]
        jawab.append(1 if sigmoid(z) >= 0.5 else 0)
    return jawab
