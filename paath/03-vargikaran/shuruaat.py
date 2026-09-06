# -*- coding: utf-8 -*-
# पाठ ३ — वर्गीकरण: हाँ या ना बताना
#
# तीन function भरने हैं. sigmoid सबसे पहले — वो एक लाइन का है.

import math


def sigmoid(z):
    """
    किसी भी संख्या को 0 और 1 के बीच लाओ.

        सिग्मॉइड(z) = 1 / (1 + e^(-z))

    e की घात के लिए math.exp() है.

    ध्यान: z बहुत बड़ी हो तो math.exp(-z) फट जाता है (OverflowError).
    इसलिए दोनों सिरे हाथ से सँभालो — नीचे ढाँचा दिया है.
    """
    if z < -500:
        return 0.0
    if z > 500:
        return 1.0

    return 0.0          # <- ठीक करो: असली सूत्र यहाँ


def shuddhata(asli, anuman):
    """
    कितना हिस्सा सही निकला.

    asli   = असली जवाब की सूची, जैसे [1, 0, 1, 1, 0]
    anuman = model के जवाब की सूची

    लौटाओ: सही जवाबों का अनुपात (0 से 1 के बीच)
    ध्यान: सूची ख़ाली हो तो शून्य से भाग मत देना.
    """
    if len(asli) == 0:
        return 0.0

    sahi = 0
    for i in range(len(asli)):
        pass            # <- ठीक करो: बराबर हों तो गिनती बढ़ाओ

    return 0.0          # <- ठीक करो: सही / कुल


def varg_batao(X, y, naye_X):
    """
    सीखो, फिर नए विद्यार्थियों के लिए 0 या 1 लौटाओ.

    X = हर पंक्ति एक विद्यार्थी: [घंटे, हाज़िरी]
    y = 1 (पास) या 0 (फेल)
    """
    n = len(X)
    vg = len(X[0])

    # ---- पैमाना (पाठ २ वाला काम) ------------------------------------------
    ausat = []
    vichalan = []
    for j in range(vg):
        stambh = [X[i][j] for i in range(n)]
        a = sum(stambh) / float(n)
        v = math.sqrt(sum((m - a) ** 2 for m in stambh) / n)
        ausat.append(a)
        vichalan.append(v)

    def badlo(pankti):
        """एक पंक्ति को उन्हीं औसत/विचलन से बदलो."""
        out = []
        for j in range(vg):
            if vichalan[j] == 0:
                out.append(pankti[j] - ausat[j])
            else:
                out.append((pankti[j] - ausat[j]) / vichalan[j])
        return out

    Xs = [badlo(p) for p in X]

    # ---- सीखो --------------------------------------------------------------
    w = [0.0] * vg
    b = 0.0
    dar = 0.1
    chakkar = 3000

    for baar in range(chakkar):
        w_dhal = [0.0] * vg
        b_dhal = 0.0

        for i in range(n):
            # 1. z निकालो (वही रेखा वाला हिसाब)
            z = b
            for j in range(vg):
                z = z + 0           # <- ठीक करो: w[j] गुणा Xs[i][j]

            # 2. सिग्मॉइड लगाकर संभावना
            p = sigmoid(z)

            # 3. ग़लती = असली - संभावना
            galti = 0               # <- ठीक करो

            # 4. ढाल में जोड़ो
            for j in range(vg):
                w_dhal[j] = w_dhal[j] + 0    # <- ठीक करो: Xs[i][j] * galti
            b_dhal = b_dhal + 0              # <- ठीक करो: galti

        # 5. क़दम रखो — यहाँ जोड़ना है, घटाना नहीं (पाठ में वजह लिखी है)
        for j in range(vg):
            w[j] = w[j] + dar * w_dhal[j] / n
        b = b + dar * b_dhal / n

    # ---- नए विद्यार्थियों का वर्ग ------------------------------------------
    jawab = []
    for pankti in naye_X:
        ps = badlo(pankti)
        z = b
        for j in range(vg):
            z = z + w[j] * ps[j]

        sambhavna = sigmoid(z)
        jawab.append(0)             # <- ठीक करो: 0.5 से ऊपर हो तो 1, वरना 0

    return jawab


# ---------------------------------------------------------------------------
# अपने प्रयोग यहाँ करो
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("सिग्मॉइड(0) =", sigmoid(0), "  (आधा आना चाहिए)")
    print("सिग्मॉइड(2) =", sigmoid(2))
    print("सिग्मॉइड(-3) =", sigmoid(-3))

    X = [[2, 40], [3, 50], [1, 30], [5, 80], [6, 90], [7, 95],
         [4, 60], [2, 35], [8, 98], [3, 45], [6, 85], [5, 70]]
    y = [0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1]

    # अपने ही आँकड़ों पर जाँचो — यहाँ शुद्धता ऊँची आनी चाहिए
    anuman = varg_batao(X, y, X)
    print("\nअपने आँकड़ों पर शुद्धता:", shuddhata(y, anuman))

    naye = [[7, 92], [1, 25], [5, 75], [2, 38]]
    print("नए विद्यार्थी:", varg_batao(X, y, naye))
    print("(1 = पास, 0 = फेल)")
