# -*- coding: utf-8 -*-
# पाठ १ का सही हल — tools/sab_jaancho.py इसे चलाकर पक्का करता है कि जाँच सही बनी है.

def hani_nikalo(x, y, m, c):
    kul = 0.0
    n = len(x)
    for i in range(n):
        anuman = m * x[i] + c
        galti = y[i] - anuman
        kul += galti * galti
    return kul / n


def seekho(x, y):
    m = 0.0
    c = 0.0
    seekhne_ki_dar = 0.01
    chakkar = 3000
    n = len(x)

    for _ in range(chakkar):
        m_dhal = 0.0
        c_dhal = 0.0
        for i in range(n):
            anuman = m * x[i] + c
            galti = y[i] - anuman
            m_dhal += -2.0 * x[i] * galti
            c_dhal += -2.0 * galti
        m_dhal /= n
        c_dhal /= n

        m -= seekhne_ki_dar * m_dhal
        c -= seekhne_ki_dar * c_dhal

    return m, c


def antim_hani_batao(x, y):
    m, c = seekho(x, y)
    return hani_nikalo(x, y, m, c)
