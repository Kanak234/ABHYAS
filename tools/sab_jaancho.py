# -*- coding: utf-8 -*-
"""
sab_jaancho.py — पूरी app की जाँच, एक हुक्म में.

किसके लिए: तुम्हारे लिए, कनक. बच्चा इसे नहीं चलाएगा.

कब चलाना है:
    - कोई नया पाठ जोड़ने के बाद
    - niyam.json में कोई नियम जोड़ने या बदलने के बाद
    - pen drive बाँटने से पहले, हमेशा

यह क्यों ज़रूरी है:
    सबसे ख़तरनाक गड़बड़ वो है जिसमें सही हल भी फेल हो जाए. सोचो — बच्चे ने
    सब कुछ ठीक किया, पर app ने कहा ग़लत है. वो अपने आप पर शक करेगा, और
    छोड़ देगा. उसे कभी पता नहीं चलेगा कि गड़बड़ app में थी.

    इसलिए यह script हर पाठ के साथ रखे हुए 'सही हल' को चलाकर पक्का करता है
    कि वो सचमुच पास होता है.

चलाओ:
    python3 tools/sab_jaancho.py
"""

import json
import os
import sys
import tempfile

yahan = os.path.dirname(os.path.abspath(__file__))
JAD = os.path.dirname(yahan)
sys.path.insert(0, os.path.join(JAD, "app"))

from mandala import Mandala, VALAYA_2, VALAYA_3          # noqa: E402
from nidan import Nidan                                  # noqa: E402
from paath import PaathSangrah                           # noqa: E402
from parikshak import Parikshak                          # noqa: E402

gintee_pass = 0
gintee_fail = 0


def jaanch(naam, shart):
    """एक जाँच — पास/फेल छापता है और गिनती रखता है."""
    global gintee_pass, gintee_fail
    if shart:
        print("  [ पास ]", naam)
        gintee_pass += 1
    else:
        print("  [ फेल ]", naam, "   <<<")
        gintee_fail += 1


# ---------------------------------------------------------------------------
print("\n" + "=" * 66)
print("  १. मंडल store")
print("=" * 66)

m = Mandala(tempfile.mkdtemp())
m.likho(VALAYA_3, "test", "a", {"x": 1})
jaanch("लिखा हुआ वापस पढ़ा जा सका", m.padho(VALAYA_3, "test", "a")["x"] == 1)
valaya, _ = m.khojo("test", "a")
jaanch("खोज बाहरी वलय से शुरू होती है", valaya == VALAYA_3)
m.chadhao(VALAYA_3, VALAYA_2, "test", "a")
valaya, _ = m.khojo("test", "a")
jaanch("record भीतरी वलय में चढ़ा", valaya == VALAYA_2)
jaanch("न मिलने पर None आता है (crash नहीं)",
       m.padho(VALAYA_3, "test", "nahi-hai") is None)

# ---------------------------------------------------------------------------
print("\n" + "=" * 66)
print("  २. निदान engine")
print("=" * 66)

n = Nidan(os.path.join(JAD, "nidan", "niyam.json"))
jaanch("नियमों की किताब खुली (%d नियम)" % len(n.niyam), len(n.niyam) > 5)


def nidan_me(sandarbh, chahiye_id):
    """निदान में यह id आया या नहीं."""
    return chahiye_id in [x["id"] for x in n.jaancho(sandarbh)]


jaanch("चिह्न उल्टा पकड़ा गया", nidan_me({
    "code": "m += seekhne_ki_dar * md\nreturn m, c", "error": "", "stdout": "",
    "natija": {"antim_hani": float("inf")}, "paath_id": "01-rekhik",
}, "chihn-ulta"))

jaanch("सीखने की दर वाली गड़बड़ पकड़ी गई", nidan_me({
    "code": "m = m - seekhne_ki_dar * md\nreturn m, c", "error": "",
    "stdout": "", "natija": {"antim_hani": float("nan")},
    "paath_id": "01-rekhik",
}, "hani-fat-gayi"))

jaanch("चिह्न उल्टा हो तो 'सीखने की दर' चुप रहती है", not nidan_me({
    "code": "m += seekhne_ki_dar * md\nreturn m, c", "error": "", "stdout": "",
    "natija": {"antim_hani": float("inf")}, "paath_id": "01-rekhik",
}, "hani-fat-gayi"))

jaanch("return न होने पर बताया गया", nidan_me({
    "code": "def f(x):\n    y = x * 2\n", "error": "", "stdout": "",
    "natija": {}, "paath_id": "01-rekhik",
}, "kuch-lautaya-nahi"))

jaanch("सही code पर कोई झूठा निदान नहीं", len(n.jaancho({
    "code": "def f(x):\n    return x * 2\n", "error": "", "stdout": "",
    "natija": {"antim_hani": 0.0001}, "paath_id": "01-rekhik",
})) == 0)

# ---------------------------------------------------------------------------
print("\n" + "=" * 66)
print("  ३. परीक्षक (code चलाने वाला)")
print("=" * 66)

p = Parikshak()
jagah = tempfile.mkdtemp()

r = p.chalao("while True:\n    pass\n", jagah)
jaanch("अनंत loop पर app नहीं अटकी", r["samay_khatam"])

r = p.chalao("print('namaste')\n", jagah)
jaanch("output सही आया", "namaste" in r["stdout"])

r = p.chalao("print(1/0)\n", jagah)
jaanch("error पकड़ा गया", "ZeroDivisionError" in r["error"])

# सबसे ज़रूरी जाँच: बदला हुआ code असल में दोबारा चलता है
mini = {"jaanch": [{"naam": "t", "bulao": "f", "do": [2], "chahiye": 4}]}
r1 = p.jaancho("def f(a):\n    return a * 2\n", mini, jagah)
r2 = p.jaancho("def f(a):\n    return a * 3\n", mini, jagah)
jaanch("code बदलने पर नतीजा भी बदला (cache वाली गड़बड़ नहीं)",
       r1["safal"] and not r2["safal"])

# ---------------------------------------------------------------------------
print("\n" + "=" * 66)
print("  ४. पाठ और उनके सही हल")
print("=" * 66)

s = PaathSangrah(os.path.join(JAD, "paath"))
jaanch("कम से कम एक पाठ मिला", len(s.sab()) > 0)

for paath in s.sab():
    pid = paath["id"]
    print("\n  पाठ: %s — %s" % (pid, paath.get("sheershak", "")))

    jaanch("    पढ़ने वाला text है", len(paath.get("padho", "")) > 200)
    jaanch("    शुरुआती code है", len(paath.get("shuruaat", "")) > 50)
    jaanch("    जाँच की सूची है", len(paath.get("jaanch", [])) > 0)

    # सही हल — हर पाठ के folder में hal.py रखो
    hal_rasta = os.path.join(paath["folder"], "hal.py")
    if not os.path.exists(hal_rasta):
        print("    [ ध्यान ] hal.py नहीं है — सही हल जाँचा नहीं जा सका")
        continue

    with open(hal_rasta, "r", encoding="utf-8") as f:
        hal = f.read()
    r = p.jaancho(hal, paath, tempfile.mkdtemp())

    if r["safal"]:
        jaanch("    सही हल सारी जाँच पास करता है", True)
    else:
        jaanch("    सही हल सारी जाँच पास करता है", False)
        for j in r.get("jaanch_parinam", []):
            if not j["safal"]:
                print("           फेल:", j["naam"])
                print("           मिला:", j.get("mila"), j.get("sandesh", ""))

# ---------------------------------------------------------------------------
print("\n" + "=" * 66)
print("  नतीजा:  %d पास,  %d फेल" % (gintee_pass, gintee_fail))
print("=" * 66)
if gintee_fail:
    print("\n  कुछ जाँच फेल हुई. बाँटने से पहले ठीक करो.\n")
    sys.exit(1)
print("\n  सब ठीक है. बाँटा जा सकता है.\n")
