# -*- coding: utf-8 -*-
# पाठ २ — जब आँकड़े एक भाषा नहीं बोलते
#
# पहले पाठ पढ़ो, और वहाँ जो प्रयोग करने को कहा है वो सचमुच करो.
# पैमाने वाला हिस्सा नीचे टिप्पणी में बंद है — पहले उसे बंद ही रहने दो.

import math


def paimana_karo(stambh):
    """
    एक column को पैमाने पर लाओ.

    लौटाओ तीन चीज़ें:  (बदला_हुआ_column, औसत, मानक_विचलन)

    औसत और मानक विचलन इसलिए लौटाने हैं कि नए आँकड़ों को भी उन्हीं से
    बदलना पड़ेगा. अगर उन्हें फेंक दिया तो नए मकान का दाम ग़लत आएगा —
    और कोई error नहीं आएगा, बस जवाब चुपचाप ग़लत होगा.
    """
    n = len(stambh)

    # 1. औसत निकालो
    ausat = 0.0          # <- ठीक करो

    # 2. मानक विचलन निकालो
    #    वर्गमूल( औसत[ (मान - औसत) का वर्ग ] )
    #    वर्गमूल के लिए math.sqrt() है
    manak_vichalan = 0.0  # <- ठीक करो

    # 3. हर मान को बदलो
    #    ध्यान: मानक विचलन शून्य हो तो भाग मत देना
    naya = []
    for maan in stambh:
        naya.append(maan)    # <- ठीक करो

    return naya, ausat, manak_vichalan


def hani_nikalo(X, y, w, b):
    """
    कई विशेषताओं के साथ हानि.

    X = पंक्तियों की सूची, हर पंक्ति एक मकान: [कमरे, क्षेत्रफल]
    w = हर विशेषता का भार: [w1, w2]
    b = अकेला जोड़ने वाला अंक

    अनुमान = w[0]*पंक्ति[0] + w[1]*पंक्ति[1] + ... + b
    """
    n = len(X)
    kul = 0.0

    for i in range(n):
        anuman = b
        for j in range(len(w)):
            anuman = anuman + 0     # <- ठीक करो: भार गुणा विशेषता

        galti = 0                   # <- असली में से अनुमान घटाओ
        kul = kul + 0               # <- वर्ग जोड़ो

    return kul / n


def bhavishyavani(X, y, naye_X):
    """
    पूरा काम — सीखो और नए मकानों का दाम बताओ.

    लौटाओ: naye_X की हर पंक्ति के लिए एक अनुमान (सूची में).
    """
    n = len(X)
    vishesh_ginti = len(X[0])

    # ---- पैमाना ----------------------------------------------------------
    # यह हिस्सा अभी बंद है. पहले ऐसे ही जाँचो और देखो क्या होता है.
    # पाठ पढ़ने के बाद इन लाइनों से # हटाओ.
    #
    # stambh_ausat = []
    # stambh_vichalan = []
    # X_paimana = [[0.0] * vishesh_ginti for _ in range(n)]
    # for j in range(vishesh_ginti):
    #     stambh = [X[i][j] for i in range(n)]
    #     naya, ausat, vichalan = paimana_karo(stambh)
    #     for i in range(n):
    #         X_paimana[i][j] = naya[i]
    #     stambh_ausat.append(ausat)
    #     stambh_vichalan.append(vichalan)
    # X = X_paimana

    # ---- सीखो -------------------------------------------------------------
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
                anuman = anuman + w[j] * X[i][j]
            galti = y[i] - anuman

            for j in range(vishesh_ginti):
                w_dhal[j] = w_dhal[j] + X[i][j] * galti
            b_dhal = b_dhal + galti

        for j in range(vishesh_ginti):
            w[j] = w[j] - seekhne_ki_dar * (-2.0 / n) * w_dhal[j]
        b = b - seekhne_ki_dar * (-2.0 / n) * b_dhal

    # ---- नए मकानों का दाम -------------------------------------------------
    jawab = []
    for pankti in naye_X:
        # नई पंक्ति को भी उन्हीं औसत/विचलन से बदलना है जो ऊपर निकले थे.
        # पैमाना खोलने पर नीचे वाली लाइनों से भी # हटाना पड़ेगा.
        #
        # badli_pankti = []
        # for j in range(vishesh_ginti):
        #     if stambh_vichalan[j] == 0:
        #         badli_pankti.append(pankti[j] - stambh_ausat[j])
        #     else:
        #         badli_pankti.append(
        #             (pankti[j] - stambh_ausat[j]) / stambh_vichalan[j])
        # pankti = badli_pankti

        anuman = b
        for j in range(vishesh_ginti):
            anuman = anuman + w[j] * pankti[j]
        jawab.append(anuman)

    return jawab


# ---------------------------------------------------------------------------
# अपने प्रयोग यहाँ करो — "चलाओ" दबाने पर यही चलता है
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    X = [[2, 800], [3, 1200], [3, 1500], [4, 1800], [5, 2400]]
    y = [24, 37, 44, 54, 71]

    kamre = [pankti[0] for pankti in X]
    print("कमरे का पैमाना:", paimana_karo(kamre))

    print("शुरुआती हानि:", hani_nikalo(X, y, [0.0, 0.0], 0.0))

    anuman = bhavishyavani(X, y, [[3, 1400], [4, 2000]])
    print("तीन कमरे 1400 वर्ग फ़ुट ->", anuman[0])
    print("चार कमरे 2000 वर्ग फ़ुट ->", anuman[1])
