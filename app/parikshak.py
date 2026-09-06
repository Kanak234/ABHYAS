# -*- coding: utf-8 -*-
"""
परीक्षक (PARIKSHAK) — बच्चे का code चलाता है और जाँचता है.

यह क्या है:
    दो काम करता है —
      chalao()  : code चलाकर उसका output दिखाता है ("चलाओ" button)
      jaancho() : code को test cases पर परखता है ("जाँचो" button)

यह ऐसा क्यों:
    Code को इसी process में exec() से चलाना सबसे आसान होता, पर ग़लत होता.
    अगर बच्चे का code अनंत loop में चला गया या crash हुआ, तो पूरी app के साथ
    जाएगा और उसका सारा लिखा हुआ काम चला जाएगा.

    इसलिए हर बार एक अलग process बनता है. वो अटके तो अटके — 10 सेकंड बाद हम
    उसे मार देते हैं, और app जस की तस चलती रहती है. बच्चे का code सुरक्षित.

    यह सिर्फ़ इंतज़ाम है, सुरक्षा-कवच (sandbox) नहीं. बच्चा अपनी ही मशीन पर
    अपना ही code चला रहा है — असली ख़तरा है नहीं. जो बचाना था वो app थी.

यह कहाँ जाता है:
    ui.py यहाँ code भेजता है ->
    यह चलाकर नतीजा लौटाता है ->
    ui.py उसे nidan.py को देता है निदान के लिए.
"""

import json
import os
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Optional

# कितनी देर इंतज़ार करें, उसके बाद process मार दें.
# 10 सेकंड इसलिए कि सीखने वाले पाठों में इससे ज़्यादा कुछ नहीं लगता,
# और अनंत loop वाला बच्चा 10 सेकंड में जान जाए कि कुछ गड़बड़ है.
SAMAY_SEEMA = 10


class Parikshak(object):
    """
    एक Parikshak object = एक पाठ की जाँच का इंतज़ाम.
    """

    def __init__(self, python_rasta=None):
        """
        python_rasta = कौन सा python इस्तेमाल करना है.

        None दो तो जो python यह app चला रहा है वही इस्तेमाल होगा.
        Pen drive वाले setup में यह portable python होगा जो साथ आया है —
        यानी बच्चे की मशीन पर python का install होना ज़रूरी नहीं.
        """
        self.python = python_rasta or sys.executable

    # -- 1. सिर्फ़ चलाओ -------------------------------------------------------

    def chalao(self, code, kaam_ki_jagah):
        """
        Code को चलाकर उसका output लौटाता है. कोई जाँच नहीं, कोई test नहीं.

        यह "चलाओ" button के लिए है — बच्चा प्रयोग कर सके, print() लगाकर
        देख सके कि अंदर क्या हो रहा है. सीखने में यह जाँच से ज़्यादा काम आता है,
        इसलिए इसे अलग रखा है.

        लौटाता है: {"stdout":…, "error":…, "samay_khatam":True/False}
        """
        # code को एक अस्थायी file में लिखते हैं, फिर उसे चलाते हैं.
        # सीधे -c से नहीं चलाते क्योंकि तब error में लाइन नंबर ठीक नहीं आते,
        # और लाइन नंबर ही वो चीज़ है जिससे बच्चा ग़लती ढूँढेगा.
        file_rasta = os.path.join(kaam_ki_jagah, "_chal_raha.py")
        with open(file_rasta, "w", encoding="utf-8") as f:
            f.write(code)

        return self._process_chalao([self.python, file_rasta], kaam_ki_jagah)

    # -- 2. जाँचो ------------------------------------------------------------

    def jaancho(self, code, paath, kaam_ki_jagah):
        """
        Code को पाठ के test cases पर परखता है.

        paath में 'jaanch' नाम की एक list होती है. हर जाँच में:
            naam    -> इस जाँच का नाम (बच्चे को दिखेगा)
            bulao   -> कौन सा function बुलाना है
            do      -> उसे क्या देना है (arguments)
            chahiye -> क्या आना चाहिए
            chhoot  -> कितनी छूट (दशमलव के लिए)

        तरीक़ा: हम एक छोटी सी "जाँच वाली file" बनाते हैं जो बच्चे के code को
        import करके सारे function बुलाती है और नतीजा JSON में छापती है.
        यह अलग process में चलती है, इसलिए बच्चे का code कुछ भी करे — हम सुरक्षित.

        लौटाता है: {"safal":…, "jaanch_parinam":[…], "natija":{…}, "error":…}
        """
        # बच्चे का code अपनी file में.
        #
        # ध्यान दो: हर बार file का नाम अलग रखा है (गिनती जोड़कर).
        # वजह — यह एक असली bug था जो पकड़ में आया. Python चली हुई file का
        # bytecode __pycache__ में रख लेता है और अगली बार वही चला देता है.
        # अगर बच्चा code बदलकर एक ही सेकंड में दोबारा जाँचे, तो file की
        # mtime वही रहती है और Python को लगता है कुछ बदला ही नहीं —
        # वो पुराना cached code चला देता है.
        #
        # नतीजा भयानक होता: बच्चा ग़लती सुधारता, पर app पुराना नतीजा दिखाती.
        # वो घंटों यह सोचकर उलझता कि "सुधारने के बाद भी वही आ रहा है".
        # अलग नाम = अलग cache entry = यह समस्या जड़ से ख़त्म.
        self._gintee = getattr(self, "_gintee", 0) + 1
        chhatra_file = os.path.join(
            kaam_ki_jagah, "_chhatra_%d.py" % self._gintee
        )
        with open(chhatra_file, "w", encoding="utf-8") as f:
            f.write(code)

        # पुरानी कोशिशों की files हटाते रहते हैं, वरना folder भरता जाएगा
        self._purani_hatao(kaam_ki_jagah)

        # जाँच की सूची अपनी file में (JSON), ताकि code में embed न करनी पड़े
        jaanch_file = os.path.join(kaam_ki_jagah, "_jaanch.json")
        with open(jaanch_file, "w", encoding="utf-8") as f:
            json.dump(paath.get("jaanch", []), f, ensure_ascii=False)

        # जाँच चलाने वाली file — यही असल में परीक्षा लेती है
        chalak_file = os.path.join(kaam_ki_jagah, "_chalak.py")
        with open(chalak_file, "w", encoding="utf-8") as f:
            f.write(self._chalak_code())

        parinam = self._process_chalao(
            [self.python, chalak_file, chhatra_file, jaanch_file],
            kaam_ki_jagah,
        )

        # चालक ने JSON छापा होगा — उसे पढ़ते हैं.
        # अगर code ही टूट गया तो JSON आएगा ही नहीं; तब error वाला रास्ता.
        try:
            data = json.loads(parinam["stdout"].strip().split("\n")[-1])
        except (ValueError, IndexError):
            return {
                "safal": False,
                "jaanch_parinam": [],
                "natija": {},
                "error": parinam["error"] or "code चला नहीं",
                "stdout": parinam["stdout"],
                "samay_khatam": parinam["samay_khatam"],
            }

        data["error"] = parinam["error"]
        data["samay_khatam"] = parinam["samay_khatam"]
        return data

    def _purani_hatao(self, kaam_ki_jagah):
        """
        पिछली कोशिशों की अस्थायी files और __pycache__ हटाता है.

        यह सफ़ाई ज़रूरी है क्योंकि हर जाँच एक नई file बनाती है. बिना इसके
        pen drive पर हज़ारों छोटी files जमा हो जातीं — और pen drive पर
        हज़ारों छोटी files का मतलब है सब कुछ धीमा.
        """
        try:
            for f in os.listdir(kaam_ki_jagah):
                if f.startswith("_chhatra_") and f.endswith(".py"):
                    n = f[len("_chhatra_"):-3]
                    # आख़िरी दो कोशिशें बची रहें, बाक़ी हटा दो
                    if n.isdigit() and int(n) < self._gintee - 1:
                        os.remove(os.path.join(kaam_ki_jagah, f))
            cache = os.path.join(kaam_ki_jagah, "__pycache__")
            if os.path.isdir(cache):
                for f in os.listdir(cache):
                    os.remove(os.path.join(cache, f))
        except OSError:
            pass          # सफ़ाई न हो पाए तो कोई बात नहीं, काम रुकना नहीं चाहिए

    # -- अंदरूनी: process चलाना ---------------------------------------------

    def _process_chalao(self, hukum, kaam_ki_jagah):
        """
        असल में process चलाने वाला function. सारी सुरक्षा यहीं है.

        Python 3.8 पर चलना है, इसलिए यहाँ subprocess.run के पुराने तरीक़े
        इस्तेमाल किए हैं — capture_output और text दोनों 3.7+ में हैं, ठीक है,
        पर encoding साफ़-साफ़ लिखी है क्योंकि Windows पर default cp1252 होता है
        और हिंदी वहाँ टूट जाती है.
        """
        try:
            p = subprocess.run(
                hukum,
                cwd=kaam_ki_jagah,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=SAMAY_SEEMA,
                encoding="utf-8",
                errors="replace",
            )
            return {
                "stdout": p.stdout or "",
                "error": p.stderr or "",
                "samay_khatam": False,
            }
        except subprocess.TimeoutExpired:
            # यहाँ पहुँचे मतलब code 10 सेकंड में ख़त्म नहीं हुआ.
            # लगभग हमेशा इसका मतलब अनंत loop है (while जिसकी शर्त कभी झूठी न हो).
            return {
                "stdout": "",
                "error": "",
                "samay_khatam": True,
            }
        except OSError as e:
            return {
                "stdout": "",
                "error": "python चलाया नहीं जा सका: " + str(e),
                "samay_khatam": False,
            }

    # -- अंदरूनी: चालक का code ----------------------------------------------

    def _chalak_code(self):
        """
        जाँच चलाने वाली छोटी file का code, text के रूप में.

        यह अलग file में इसलिए है (और यहाँ string में लिखा है) ताकि बच्चे के
        folder में एक और स्थायी file न रखनी पड़े — हर जाँच पर बन जाती है,
        और अगली बार बदल जाती है.

        यह छपाई (print) के आख़िर में एक ही लाइन का JSON छापता है. ऊपर जो कुछ
        भी बच्चे ने print किया, वो अलग से दिखता रहता है — इसलिए हम हमेशा
        आख़िरी लाइन ही पढ़ते हैं.
        """
        return '''# -*- coding: utf-8 -*-
# यह ABHYAS की अपनी file है, अपने आप बनती है. इसे बदलने की ज़रूरत नहीं.
import sys
sys.dont_write_bytecode = True   # दूसरी सुरक्षा: cache बने ही नहीं

import json, os, importlib.util, traceback, math

chhatra_file = sys.argv[1]
jaanch_file  = sys.argv[2]

with open(jaanch_file, "r", encoding="utf-8") as f:
    jaanch_suchi = json.load(f)

parinam = {"safal": False, "jaanch_parinam": [], "natija": {}}

def barabar(mila, chahiye, chhoot):
    """दो values बराबर हैं या नहीं — दशमलव के लिए छूट के साथ."""
    if isinstance(chahiye, (int, float)) and isinstance(mila, (int, float)):
        if mila != mila:          # nan
            return False
        return abs(float(mila) - float(chahiye)) <= chhoot
    if isinstance(chahiye, (list, tuple)):
        if not isinstance(mila, (list, tuple)) or len(mila) != len(chahiye):
            return False
        for a, b in zip(mila, chahiye):
            if not barabar(a, b, chhoot):
                return False
        return True
    return mila == chahiye

try:
    # बच्चे के code को module की तरह import करते हैं
    spec = importlib.util.spec_from_file_location("chhatra", chhatra_file)
    chhatra = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(chhatra)
except Exception:
    print(traceback.format_exc(), file=sys.stderr)
    print(json.dumps(parinam, ensure_ascii=False))
    sys.exit(0)

sab_safal = True
for j in jaanch_suchi:
    ek = {"naam": j.get("naam", ""), "safal": False, "mila": None}
    try:
        fn = getattr(chhatra, j["bulao"], None)
        if fn is None:
            ek["sandesh"] = j["bulao"] + " नाम का function मिला ही नहीं"
            sab_safal = False
            parinam["jaanch_parinam"].append(ek)
            continue

        mila = fn(*j.get("do", []))

        # numpy की चीज़ों को सादी Python list में बदलते हैं ताकि JSON में जा सकें
        try:
            if hasattr(mila, "tolist"):
                mila = mila.tolist()
            elif isinstance(mila, tuple):
                mila = [x.tolist() if hasattr(x, "tolist") else x for x in mila]
        except Exception:
            pass

        ek["mila"] = mila
        chhoot = j.get("chhoot", 0.001)

        if "chahiye" in j:
            ek["safal"] = barabar(mila, j["chahiye"], chhoot)
        elif "sangrah" in j:
            # जाँच नहीं, सिर्फ़ नतीजा इकट्ठा करना — निदान इसी को देखेगा
            parinam["natija"][j["sangrah"]] = mila if not isinstance(mila, (list, tuple)) else mila
            ek["safal"] = True
        else:
            ek["safal"] = mila is not None

        if not ek["safal"]:
            sab_safal = False

    except Exception as e:
        ek["sandesh"] = type(e).__name__ + ": " + str(e)
        print(traceback.format_exc(), file=sys.stderr)
        sab_safal = False

    parinam["jaanch_parinam"].append(ek)

parinam["safal"] = sab_safal and len(jaanch_suchi) > 0
print(json.dumps(parinam, ensure_ascii=False, default=str))
'''


# ---------------------------------------------------------------------------
# जाँच: python3 app/parikshak.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    p = Parikshak()
    jagah = tempfile.mkdtemp()

    # स्थिति 1: सही code
    sahi = "def jodo(a, b):\n    return a + b\n"
    paath = {"jaanch": [
        {"naam": "2+3 = 5", "bulao": "jodo", "do": [2, 3], "chahiye": 5},
        {"naam": "10+5 = 15", "bulao": "jodo", "do": [10, 5], "chahiye": 15},
    ]}
    r = p.jaancho(sahi, paath, jagah)
    print("सही code ->", "पास" if r["safal"] else "फेल")

    # स्थिति 2: ग़लत code
    galat = "def jodo(a, b):\n    return a - b\n"
    r = p.jaancho(galat, paath, jagah)
    print("ग़लत code ->", "पास" if r["safal"] else "फेल",
          "| पहली जाँच में मिला:", r["jaanch_parinam"][0]["mila"])

    # स्थिति 3: अनंत loop
    loop = "while True:\n    pass\n"
    r = p.chalao(loop, jagah)
    print("अनंत loop ->", "समय ख़त्म हुआ, app बची" if r["samay_khatam"] else "गड़बड़")
