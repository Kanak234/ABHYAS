# -*- coding: utf-8 -*-
"""
पाठ (PAATH) — पाठों को folder से पढ़ने वाला हिस्सा.

यह क्या है:
    paath/ folder में जितने भी पाठ पड़े हैं, उन्हें पढ़कर एक क्रम में लगाता है.

यह ऐसा क्यों — और यही इस project की सबसे ज़रूरी बात है:
    पाठ code में कहीं नहीं लिखे हैं. वो सिर्फ़ folder में पड़ी data files हैं.

    इसका मतलब: नया पाठ जोड़ने के लिए app को छूना नहीं पड़ता. बस एक folder
    बनाओ, उसमें तीन files डालो, बस. App अगली बार खुलते ही उसे उठा लेगी.

    यही वो चीज़ है जो इस app को दो-तीन साल चलने लायक बनाती है. Code जम जाएगा
    और वैसा ही रहेगा; content बदलता रहेगा. दोनों की उम्र अलग-अलग है, इसलिए
    दोनों को अलग रखा है.

एक पाठ का folder ऐसा दिखता है:

    paath/01-rekhik/
        paath.json     -> पाठ की जानकारी और जाँच की सूची
        padho.md       -> जो बच्चा पढ़ेगा
        shuruaat.py    -> code box में पहले से भरा हुआ ढाँचा

यह कहाँ जाता है:
    ui.py यहाँ से पाठ माँगता है और परदे पर दिखाता है.
"""

import json
import os
from typing import Any, Dict, List, Optional


class PaathSangrah(object):
    """सारे पाठों का संग्रह — एक बार पढ़ा जाता है, app के शुरू में."""

    def __init__(self, paath_folder):
        self.folder = paath_folder
        self.paath_suchi = []
        self._padho_sab()

    def _padho_sab(self):
        """
        paath/ के हर folder को देखता है और वैध पाठों को सूची में लगाता है.

        क्रम folder के नाम से तय होता है — इसीलिए नाम 01-, 02- से शुरू होते हैं.
        ऐसा इसलिए कि क्रम बदलना हो तो सिर्फ़ folder का नाम बदलो, कोई सूची-file
        अलग से नहीं सँभालनी पड़े. एक चीज़ कम टूटने के लिए.
        """
        if not os.path.isdir(self.folder):
            return

        naam_suchi = sorted(os.listdir(self.folder))
        for naam in naam_suchi:
            paath_rasta = os.path.join(self.folder, naam)
            if not os.path.isdir(paath_rasta):
                continue

            json_rasta = os.path.join(paath_rasta, "paath.json")
            if not os.path.exists(json_rasta):
                continue        # बिना paath.json के folder को चुपचाप छोड़ दो

            try:
                with open(json_rasta, "r", encoding="utf-8") as f:
                    paath = json.load(f)
            except (ValueError, IOError, OSError):
                continue        # ख़राब पाठ पूरी app न रोके

            paath["id"] = paath.get("id", naam)
            paath["folder"] = paath_rasta
            paath["padho"] = self._file_padho(paath_rasta, "padho.md")
            paath["shuruaat"] = self._file_padho(paath_rasta, "shuruaat.py")
            self.paath_suchi.append(paath)

    def _file_padho(self, folder, naam):
        """एक file पढ़ता है; न मिले तो ख़ाली text."""
        rasta = os.path.join(folder, naam)
        if not os.path.exists(rasta):
            return ""
        try:
            with open(rasta, "r", encoding="utf-8") as f:
                return f.read()
        except (IOError, OSError):
            return ""

    # -- बाहर से इस्तेमाल होने वाले ------------------------------------------

    def sab(self):
        """सारे पाठों की सूची."""
        return self.paath_suchi

    def ek(self, paath_id):
        """id से एक पाठ; न मिले तो None."""
        for p in self.paath_suchi:
            if p["id"] == paath_id:
                return p
        return None

    def agla(self, mandala):
        """
        बच्चे को अगला कौन सा पाठ करना चाहिए, यह तय करता है.

        तरीक़ा सीधा है: पहला ऐसा पाठ जो अभी पूरा नहीं हुआ.
        प्रगति मंडल के वलय-2 में रहती है (क्योंकि वो हफ़्तों-महीनों की चीज़ है,
        घंटों की नहीं).

        जान-बूझकर कोई ताला (lock) नहीं लगाया — बच्चा चाहे तो किसी भी पाठ पर
        कूद सकता है. ताला लगाने से सीखने वाला रुकता है, बढ़ता नहीं.
        """
        for p in self.paath_suchi:
            pragati = mandala.padho("valaya-2", "pragati", p["id"])
            if pragati is None or not pragati.get("poora"):
                return p
        return None     # सारे पाठ हो गए


# ---------------------------------------------------------------------------
# जाँच: python3 app/paath.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    yahan = os.path.dirname(os.path.abspath(__file__))
    s = PaathSangrah(os.path.join(yahan, "..", "paath"))
    print("पाठ मिले:", len(s.sab()))
    for p in s.sab():
        print("  -", p["id"], "|", p.get("sheershak", ""),
              "| जाँच:", len(p.get("jaanch", [])))
