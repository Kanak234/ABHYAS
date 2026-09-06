# -*- coding: utf-8 -*-
"""
निदान (NIDAN) — बच्चे की ग़लती पहचानने वाला engine.

यह क्या है:
    बच्चे का code, उसका error, और उसका नतीजा — तीनों देखकर यह बताता है कि
    असल में गड़बड़ कहाँ है, और उसे हिंदी में समझाता है.

यह ऐसा क्यों (सबसे ज़रूरी बात):
    इसमें कोई AI model नहीं चलता. एक भी नहीं.
    वजह — U processor और 4 GB RAM वाले laptop पर कोई भी LLM चलाना यातना है.
    इसलिए सारी "समझ" पहले से यहाँ नियमों की शक्ल में रखी है, और सारी
    explanation पहले से लिखी हुई है (nidan/niyam.json में).

    असल AI का काम build के वक़्त हुआ है, तुम्हारी i9 मशीन पर — जब तुमने
    ये explanations बनवाईं. बच्चे की मशीन पर सिर्फ़ मिलान (matching) होता है,
    जो microseconds में हो जाता है.

    नतीजा: बच्चे को लगता है कोई देख रहा है और समझा रहा है — और यह झूठ नहीं है.
    ग़लती असल में उसके चलाए हुए code से पकड़ी गई है. बस सोचना पहले हो चुका है.

यह कहाँ से आता है / कहाँ जाता है:
    grader.py कोड चलाकर नतीजा यहाँ भेजता है ->
    यह निदान लौटाता है -> ui.py उसे बच्चे को दिखाता है.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional


class Nidan(object):
    """
    नियमों की किताब को memory में रखता है और उस पर मिलान चलाता है.

    किताब एक बार खुलती है, app के शुरू में. उसके बाद हर जाँच बस
    list पर एक loop है — इसलिए सबसे कमज़ोर मशीन पर भी तुरंत चलता है.
    """

    def __init__(self, niyam_file):
        """
        niyam_file = nidan/niyam.json का रास्ता.

        अगर file न मिले या ख़राब हो, तो engine ख़ाली नियमों के साथ चलेगा —
        app फिर भी काम करेगी, बस explanation सामान्य वाली मिलेगी.
        Crash करने से यह बेहतर है.
        """
        self.niyam = []
        try:
            with open(niyam_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.niyam = data.get("niyam", [])
        except (IOError, OSError, ValueError):
            self.niyam = []

    # -- मुख्य काम ----------------------------------------------------------

    def jaancho(self, sandarbh):
        """
        निदान करने वाला मुख्य function.

        sandarbh (context) एक dict है जिसमें ये चीज़ें आती हैं:
            code        -> बच्चे ने जो लिखा (पूरा text)
            error       -> Python का error text, न हो तो ""
            stdout      -> code का output
            natija      -> test चलाने पर जो values मिलीं (dict)
            paath_id    -> कौन सा पाठ चल रहा है

        लौटाता है: मिले हुए निदानों की list, सबसे ज़रूरी सबसे ऊपर.
        एक से ज़्यादा इसलिए कि अक्सर एक साथ दो चीज़ें ग़लत होती हैं.
        """
        mile = []
        for niyam in self.niyam:
            if self._niyam_lagta_hai(niyam, sandarbh):
                mile.append({
                    "id": niyam.get("id", "?"),
                    "sheershak": niyam.get("sheershak", ""),
                    "vyakhya": niyam.get("vyakhya", ""),
                    "sanket": niyam.get("sanket", ""),
                    "gambhirta": niyam.get("gambhirta", 5),
                })

        # गंभीरता के हिसाब से क्रम — 1 सबसे गंभीर.
        # ऐसा इसलिए कि अगर code चला ही नहीं (syntax error), तो उसे पहले
        # दिखाना है; "scaling नहीं किया" वाली बात बाद की है.
        mile.sort(key=lambda x: x["gambhirta"])

        # एक बार में तीन से ज़्यादा मत दिखाओ. बच्चा दस बातें पढ़कर घबरा जाएगा,
        # और घबराया हुआ बच्चा छोड़ देता है — यही तो रोकना है.
        return mile[:3]

    # -- मिलान का असली logic ------------------------------------------------

    def _niyam_lagta_hai(self, niyam, s):
        """
        एक नियम इस स्थिति पर लागू होता है या नहीं, यह तय करता है.

        हर नियम में 'shart' (शर्तें) होती हैं. सारी शर्तें पूरी हों तभी
        नियम लगता है — यानी AND, OR नहीं. इससे नियम सटीक रहते हैं और
        ग़लत निदान कम आते हैं (ग़लत निदान सही निदान न देने से ज़्यादा नुक़सान करता है).
        """
        shart = niyam.get("shart", {})

        # पाठ-विशेष नियम — कुछ नियम सिर्फ़ एक ही पाठ पर लागू होते हैं
        keval_paath = shart.get("keval_paath")
        if keval_paath and s.get("paath_id") != keval_paath:
            return False

        # 1. error text में कोई शब्द है क्या
        error_me = shart.get("error_me")
        if error_me:
            if error_me.lower() not in (s.get("error") or "").lower():
                return False

        # 2. code में कोई pattern है क्या (regex)
        #
        # एक pattern भी दे सकते हो, या कई की list. list देने पर सबका मिलना
        # ज़रूरी है. यह सुविधा इसलिए जोड़ी कि सटीक निदान के लिए अक्सर दो-तीन
        # बातें एक साथ जाँचनी पड़ती हैं — और एक pattern में सब ठूँसने से
        # regex ऐसी बन जाती है जिसे छह महीने बाद कोई नहीं पढ़ पाएगा.
        code_me = shart.get("code_me")
        if code_me:
            for pat in self._suchi_banao(code_me):
                if not re.search(pat, s.get("code") or "", re.MULTILINE):
                    return False

        # 3. code में कोई चीज़ *नहीं* है क्या — यह सबसे काम का नियम-प्रकार है,
        #    क्योंकि सीखने वाले की ग़लती अक्सर "कुछ लिखा ही नहीं" होती है.
        #    list दो तो कोई भी मिल जाने पर नियम नहीं लगेगा.
        code_me_nahi = shart.get("code_me_nahi")
        if code_me_nahi:
            for pat in self._suchi_banao(code_me_nahi):
                if re.search(pat, s.get("code") or "", re.MULTILINE):
                    return False

        # 4. नतीजे की कोई value बहुत बड़ी / nan है क्या
        #    (learning rate ज़्यादा होने की पहचान इसी से होती है)
        natija_bigda = shart.get("natija_bigda")
        if natija_bigda:
            maan = (s.get("natija") or {}).get(natija_bigda)
            if not self._bigda_hua(maan):
                return False

        # 5. कोई value सही सीमा के बाहर है क्या
        seema = shart.get("seema")
        if seema:
            maan = (s.get("natija") or {}).get(seema.get("kya"))
            if maan is None:
                return False
            try:
                maan = float(maan)
            except (TypeError, ValueError):
                return False
            if "se_zyada" in seema and not maan > seema["se_zyada"]:
                return False
            if "se_kam" in seema and not maan < seema["se_kam"]:
                return False

        return True

    def _suchi_banao(self, cheez):
        """
        एक चीज़ हो या कई — दोनों को list बना देता है.

        इससे niyam.json में दोनों तरीक़े चलते हैं:
            "code_me": "return"                  (एक)
            "code_me": ["return", "for"]         (कई)
        नियम लिखने वाले को सोचना न पड़े कि कौन सा तरीक़ा सही है.
        """
        if isinstance(cheez, (list, tuple)):
            return list(cheez)
        return [cheez]

    def _bigda_hua(self, maan):
        """
        कोई नतीजा 'बिगड़ा हुआ' है या नहीं — यानी nan, inf, या बेतुकी बड़ी.

        Gradient descent में सीखने की दर ज़्यादा रखने पर हानि फटकर nan या
        inf हो जाती है. यह सीखने वालों की सबसे उलझाने वाली ग़लती है, क्योंकि
        error कोई नहीं आता — बस नतीजा बेतुका आता है. इसलिए इसे अलग से
        पकड़ना ज़रूरी था.

        सूची भी चलती है: भविष्यवाणी अक्सर कई मानों की सूची होती है, और
        उनमें से एक भी बिगड़ा हो तो पूरा नतीजा बिगड़ा माना जाएगा. यह
        सुविधा इसलिए जोड़ी कि बिना इसके सिर्फ़ अकेली संख्या पर नज़र रखी
        जा सकती थी, और तब वो नियम चुप रह जाते जिन्हें बोलना चाहिए था.
        """
        if maan is None:
            return False

        # सूची हो तो हर सदस्य को जाँचो — एक भी बिगड़ा तो बस
        if isinstance(maan, (list, tuple)):
            for ek in maan:
                if self._bigda_hua(ek):
                    return True
            return False

        try:
            maan = float(maan)
        except (TypeError, ValueError):
            return False
        if maan != maan:            # nan की पहचान: nan खुद के बराबर नहीं होता
            return True
        if maan in (float("inf"), float("-inf")):
            return True
        if abs(maan) > 1e10:
            return True
        return False


# ---------------------------------------------------------------------------
# जाँच: python3 app/nidan.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    yahan = os.path.dirname(os.path.abspath(__file__))
    n = Nidan(os.path.join(yahan, "..", "nidan", "niyam.json"))
    print("नियम लोड हुए:", len(n.niyam))

    # स्थिति 1: बच्चे ने return लिखा ही नहीं
    parinam = n.jaancho({
        "code": "def dhalaan(x, y):\n    m = 0.5\n",
        "error": "",
        "stdout": "",
        "natija": {},
        "paath_id": "01-rekhik",
    })
    print("\nस्थिति 1 (return नहीं):")
    for p in parinam:
        print("  -", p["sheershak"])

    # स्थिति 2: learning rate बहुत ज़्यादा, loss फट गया
    parinam = n.jaancho({
        "code": "seekhne_ki_dar = 5.0\nreturn m, c",
        "error": "",
        "stdout": "",
        "natija": {"antim_hani": float("nan")},
        "paath_id": "01-rekhik",
    })
    print("\nस्थिति 2 (loss फट गया):")
    for p in parinam:
        print("  -", p["sheershak"])
