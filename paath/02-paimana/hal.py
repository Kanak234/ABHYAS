# -*- coding: utf-8 -*-
# पाठ २ का सही हल — यह बच्चों वाले package में नहीं जाता.
# tools/sab_jaancho.py इसे चलाकर पक्का करता है कि जाँच सही बनी है.

import math


def paimana_karo(stambh):
    n = len(stambh)
    ausat = sum(stambh) / float(n)

    varg_kul = 0.0
    for maan in stambh:
        varg_kul += (maan - ausat) ** 2
    manak_vichalan = math.sqrt(varg_kul / n)

    naya = []
    for maan in stambh:
        if manak_vichalan == 0:
            naya.append(maan - ausat)
        else:
            naya.append((maan - ausat) / manak_vichalan)

    return naya, ausat, manak_vichalan


def hani_nikalo(X, y, w, b):
    n = len(X)
    kul = 0.0
    for i in range(n):
        anuman = b
        for j in range(len(w)):
            anuman += w[j] * X[i][j]
        galti = y[i] - anuman
        kul += galti * galti
    return kul / n


def bhavishyavani(X, y, naye_X):
    n = len(X)
    vishesh_ginti = len(X[0])

    stambh_ausat = []
    stambh_vichalan = []
    X_paimana = [[0.0] * vishesh_ginti for _ in range(n)]
    for j in range(vishesh_ginti):
        stambh = [X[i][j] for i in range(n)]
        naya, ausat, vichalan = paimana_karo(stambh)
        for i in range(n):
            X_paimana[i][j] = naya[i]
        stambh_ausat.append(ausat)
        stambh_vichalan.append(vichalan)
    X = X_paimana

    w = [0.0] * vishesh_ginti
    b = 0.0
    seekhne_ki_dar = 0.05
    chakkar = 2000

    for baar in range(chakkar):
        w_dhal = [0.0] * vishesh_ginti
        b_dhal = 0.0
        for i in range(n):
            anuman = b
            for j in range(vishesh_ginti):
                anuman += w[j] * X[i][j]
            galti = y[i] - anuman
            for j in range(vishesh_ginti):
                w_dhal[j] += X[i][j] * galti
            b_dhal += galti
        for j in range(vishesh_ginti):
            w[j] = w[j] - seekhne_ki_dar * (-2.0 / n) * w_dhal[j]
        b = b - seekhne_ki_dar * (-2.0 / n) * b_dhal

    jawab = []
    for pankti in naye_X:
        badli = []
        for j in range(vishesh_ginti):
            if stambh_vichalan[j] == 0:
                badli.append(pankti[j] - stambh_ausat[j])
            else:
                badli.append((pankti[j] - stambh_ausat[j]) / stambh_vichalan[j])
        anuman = b
        for j in range(vishesh_ginti):
            anuman += w[j] * badli[j]
        jawab.append(anuman)

    return jawab
