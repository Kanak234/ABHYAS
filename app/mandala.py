# -*- coding: utf-8 -*-
"""
मंडल (MANDALA) — ABHYAS का data store.

यह क्या है:
    Data को "कितनी तेज़ी से बदलता है" के हिसाब से चार परतों (वलय) में बाँटा गया है,
    ठीक वैसे जैसे मंडल में संकेंद्रित वृत्त होते हैं — केंद्र स्थिर, बाहर चंचल।

        बिंदु      -> कभी नहीं बदलता  (पहचान, config)          read-only
        वलय-1      -> महीनों में बदलता (जो सीखा और टिक गया)
        वलय-2      -> हफ़्तों में बदलता (कौन सा पाठ कहाँ तक हुआ)
        वलय-3      -> घंटों में मरता   (आज का कच्चा काम, attempts)

यह ऐसा क्यों:
    Memory अपने आप साफ़ होती रहे, बिना किसी को delete का फ़ैसला लिए। वलय-3 अपनी
    उम्र पूरी करके ख़ुद मिट जाता है; जो चीज़ बार-बार काम आई वो अंदर चढ़ जाती है।
    इसलिए दो साल बाद भी यह folder फूलेगा नहीं.

यह कहाँ जाता है:
    ui.py इसे progress दिखाने के लिए पढ़ता है,
    grader.py हर attempt यहीं वलय-3 में लिखता है,
    और paath.py अगला पाठ चुनने के लिए वलय-2 देखता है.

Python 3.8 पर चलना ज़रूरी है (Windows 7 वाले laptop) — इसलिए यहाँ कोई नई syntax
इस्तेमाल नहीं की गई: न match, न builtin generics (list[str]), न walrus.
"""

import json
import os
import time
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# वलय के नाम एक ही जगह रखे हैं ताकि कहीं spelling बदलनी पड़े तो एक ही लाइन बदले।
# बाक़ी पूरी file और बाक़ी modules इन्हीं constants को इस्तेमाल करते हैं।
# ---------------------------------------------------------------------------
BINDU = "bindu"            # केंद्र — स्थिर
VALAYA_1 = "valaya-1"      # दीर्घ स्मृति
VALAYA_2 = "valaya-2"      # प्रगति
VALAYA_3 = "valaya-3"      # आज का काम

# हर वलय कितने दिन बाद अपने आप साफ़ हो जाए।
# None का मतलब — कभी साफ़ मत करो।
# यही वो एक table है जो "memory अपने आप घटती रहे" वाला पूरा काम करता है।
AAYU_DIN = {
    BINDU: None,
    VALAYA_1: None,
    VALAYA_2: 365,
    VALAYA_3: 7,
}


class Mandala(object):
    """
    मंडल store का एक object = एक बच्चे का पूरा data.

    सब कुछ सादी JSON files में रहता है — कोई database नहीं, कोई server नहीं.
    वजह: pen drive पर चलना है, Windows 7 पर चलना है, और दो साल बाद भी खुलना है.
    JSON हर Python में खुलेगा; sqlite भी खुलता, पर JSON को बच्चा ख़ुद notepad में
    खोलकर देख सकता है — और यही इस project के लिए ज़्यादा ज़रूरी है.
    """

    def __init__(self, jad):
        """
        jad = मंडल folder का पूरा रास्ता (root).
        बनाते ही चारों वलय के folder बना देते हैं, ताकि आगे कहीं भी
        "folder नहीं मिला" वाली गलती न आए.
        """
        self.jad = jad
        for valaya in (BINDU, VALAYA_1, VALAYA_2, VALAYA_3):
            os.makedirs(os.path.join(self.jad, valaya), exist_ok=True)

    # -- अंदरूनी सहायक ------------------------------------------------------

    def _rasta(self, valaya, khand, naam):
        """
        किसी एक record की file का पूरा रास्ता बनाता है.

        khand = "खंड" यानी विषय (जैसे 'ml', 'python'). मंडल में जैसे त्रिज्या के
        साथ हिस्से कटे होते हैं, वैसे ही यहाँ एक वलय के अंदर कई खंड होते हैं.
        इससे बाद में "सिर्फ़ ML वाला data दिखाओ" करना आसान रहेगा.
        """
        thikana = os.path.join(self.jad, valaya, khand)
        os.makedirs(thikana, exist_ok=True)
        return os.path.join(thikana, naam + ".json")

    # -- लिखना --------------------------------------------------------------

    def likho(self, valaya, khand, naam, samagri):
        """
        एक record लिखता है (पूरा बदल देता है).

        हर record के साथ 'likha_gaya' (timestamp) अपने आप जुड़ता है — यही
        बाद में safai() को बताता है कि यह कितना पुराना हो चुका है.
        समय epoch seconds में रखा है, किसी भी locale/timezone में सुरक्षित.
        """
        record = dict(samagri)
        record["likha_gaya"] = time.time()
        rasta = self._rasta(valaya, khand, naam)

        # पहले temp file में लिखकर फिर rename करते हैं.
        # वजह: बिजली तुम्हारे इलाक़े में भरोसेमंद नहीं है. अगर लिखते वक़्त
        # बिजली गई तो असली file अधूरी नहीं बचेगी — या पुरानी पूरी रहेगी,
        # या नई पूरी. आधी-अधूरी कभी नहीं.
        temp = rasta + ".tmp"
        with open(temp, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        if os.path.exists(rasta):
            os.remove(rasta)   # Windows पर rename तभी चलता है जब target न हो
        os.rename(temp, rasta)
        return rasta

    def jodo(self, valaya, khand, naam, kadi):
        """
        एक list-type record में नई कड़ी जोड़ता है (पूरा बदले बिना).

        इस्तेमाल: attempts का इतिहास. हर बार बच्चा 'जाँचो' दबाए, एक कड़ी जुड़े.
        list को 200 पर काट देते हैं ताकि यह file कभी बेकाबू न बढ़े.
        """
        purana = self.padho(valaya, khand, naam)
        if purana is None:
            purana = {"kadiyan": []}
        kadiyan = purana.get("kadiyan", [])
        kadi = dict(kadi)
        kadi["samay"] = time.time()
        kadiyan.append(kadi)
        purana["kadiyan"] = kadiyan[-200:]
        return self.likho(valaya, khand, naam, purana)

    # -- पढ़ना ---------------------------------------------------------------

    def padho(self, valaya, khand, naam):
        """
        एक record पढ़ता है. न मिले तो None — exception नहीं.

        यहाँ जान-बूझकर हर गलती को चुपचाप None बनाया है. वजह: यह app बच्चे के
        सामने crash नहीं होनी चाहिए. Progress file ख़राब हो गई तो बुरा है,
        पर app का न खुलना उससे बहुत बुरा है.
        """
        rasta = self._rasta(valaya, khand, naam)
        if not os.path.exists(rasta):
            return None
        try:
            with open(rasta, "r", encoding="utf-8") as f:
                return json.load(f)
        except (ValueError, IOError, OSError):
            return None

    def khojo(self, khand, naam):
        """
        मंडल का मुख्य पढ़ने का तरीक़ा — बाहर से अंदर की ओर.

        क्रम: वलय-3 -> वलय-2 -> वलय-1 -> बिंदु
        यानी सबसे पहले सबसे ताज़ा देखो. ज़्यादातर सवाल वहीं निपट जाएँगे और
        अंदर की परतें छूनी ही नहीं पड़ेंगी. यही मंडल का पूरा फ़ायदा है.
        """
        for valaya in (VALAYA_3, VALAYA_2, VALAYA_1, BINDU):
            mila = self.padho(valaya, khand, naam)
            if mila is not None:
                return valaya, mila
        return None, None

    def suchi(self, valaya, khand):
        """उस खंड के सारे record के नाम लौटाता है (बिना .json के)."""
        thikana = os.path.join(self.jad, valaya, khand)
        if not os.path.isdir(thikana):
            return []
        naam = []
        for f in os.listdir(thikana):
            if f.endswith(".json"):
                naam.append(f[:-5])
        naam.sort()
        return naam

    # -- चढ़ना और मिटना -------------------------------------------------------

    def chadhao(self, se_valaya, tak_valaya, khand, naam):
        """
        एक record को बाहरी वलय से भीतरी वलय में चढ़ाता है (promote).

        कब इस्तेमाल होता है: जब बच्चा कोई पाठ पूरा कर ले, तो उसका नतीजा
        वलय-3 (जो 7 दिन में मिट जाता) से वलय-2 में चढ़ जाता है — यानी
        अस्थायी काम स्थायी प्रगति बन जाता है.

        यही वो जगह है जहाँ "जो काम आया वो बचता है, बाक़ी मिटता है" वाला
        नियम असल में लागू होता है.
        """
        samagri = self.padho(se_valaya, khand, naam)
        if samagri is None:
            return False
        self.likho(tak_valaya, khand, naam, samagri)
        purana = self._rasta(se_valaya, khand, naam)
        if os.path.exists(purana):
            os.remove(purana)
        return True

    def safai(self):
        """
        उम्र पूरी कर चुके record मिटाता है.

        app खुलते ही एक बार चलता है (__main__.py से). कोई cron नहीं, कोई
        background thread नहीं — क्योंकि 4 GB RAM वाले laptop पर हर चालू
        thread की क़ीमत है.

        लौटाता है: कितनी file मिटीं (सिर्फ़ जानकारी के लिए).
        """
        mite = 0
        ab = time.time()
        for valaya, din in AAYU_DIN.items():
            if din is None:
                continue                      # बिंदु और वलय-1 कभी नहीं मिटते
            seema = din * 24 * 60 * 60        # दिन को seconds में बदला
            thikana = os.path.join(self.jad, valaya)
            if not os.path.isdir(thikana):
                continue
            for khand in os.listdir(thikana):
                khand_rasta = os.path.join(thikana, khand)
                if not os.path.isdir(khand_rasta):
                    continue
                for f in os.listdir(khand_rasta):
                    if not f.endswith(".json"):
                        continue
                    poora = os.path.join(khand_rasta, f)
                    try:
                        # file की अपनी mtime इस्तेमाल कर रहे हैं, अंदर के
                        # timestamp की नहीं — क्योंकि file ख़राब हो तब भी
                        # यह काम करता रहे.
                        if ab - os.path.getmtime(poora) > seema:
                            os.remove(poora)
                            mite += 1
                    except OSError:
                        pass
        return mite


# ---------------------------------------------------------------------------
# नीचे वाला हिस्सा तभी चलता है जब इस file को सीधे python से चलाया जाए.
# बच्चे के लिए नहीं है — तुम्हारे लिए है, यह जाँचने के लिए कि store ठीक है.
#     python3 app/mandala.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import tempfile

    jaanch_jagah = tempfile.mkdtemp()
    m = Mandala(jaanch_jagah)

    m.likho(VALAYA_3, "ml", "attempt", {"paath": "01", "safal": False})
    valaya, mila = m.khojo("ml", "attempt")
    assert valaya == VALAYA_3, "खोज बाहरी वलय से शुरू नहीं हुई"
    assert mila["safal"] is False

    m.chadhao(VALAYA_3, VALAYA_2, "ml", "attempt")
    valaya, mila = m.khojo("ml", "attempt")
    assert valaya == VALAYA_2, "record चढ़ा नहीं"

    m.jodo(VALAYA_3, "ml", "itihas", {"kya": "pehli koshish"})
    m.jodo(VALAYA_3, "ml", "itihas", {"kya": "dusri koshish"})
    itihas = m.padho(VALAYA_3, "ml", "itihas")
    assert len(itihas["kadiyan"]) == 2

    print("मंडल ठीक है — सारी जाँच पास हुई.")
