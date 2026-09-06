# -*- coding: utf-8 -*-
"""
अभ्यास (ABHYAS) — शुरुआत यहाँ से होती है.

चलाने का तरीक़ा:
    Windows पर  : START.bat पर दो बार click
    Linux पर    : ./start.sh
    सीधे        : python3 app

यह file क्या करती है:
    1. जाँचती है कि Python का version काम लायक है
    2. app के module को रास्ते में जोड़ती है
    3. खिड़की खोलती है
    4. कुछ भी टूटे तो हिंदी में बताती है, अंग्रेज़ी का traceback फेंककर नहीं

चौथा बिंदु सबसे ज़रूरी है. अगर बच्चे के सामने काला traceback आया तो वो
समझेगा कि उसने कुछ तोड़ दिया, और डरकर बंद कर देगा. जो भी टूटे, हिंदी में
बताना है — और यह बताना है कि उसकी ग़लती नहीं है.
"""

import os
import sys

# ---------------------------------------------------------------------------
# 1. Python का version
#
# 3.6 सबसे नीचे की सीमा रखी है क्योंकि उससे पहले f-string नहीं थी और
# dict का क्रम पक्का नहीं था. Windows 7 वाले laptop पर 3.8 चलेगा — वो
# आख़िरी version है जो Windows 7 को support करता है, इसलिए पूरा code
# 3.8 के हिसाब से लिखा गया है और उससे नई कोई syntax कहीं इस्तेमाल नहीं की.
# ---------------------------------------------------------------------------
if sys.version_info < (3, 6):
    print("यह app चलाने के लिए Python 3.6 या उससे नया चाहिए.")
    print("तुम्हारे पास है:", sys.version.split()[0])
    print("\nसाथ आए हुए python folder से चलाओ — START.bat वही करता है.")
    sys.exit(1)


def mukhya():
    """असली शुरुआत."""
    # इस file का folder = app/ ; उससे एक ऊपर = ABHYAS/
    app_folder = os.path.dirname(os.path.abspath(__file__))
    jad = os.path.dirname(app_folder)

    # app/ को import रास्ते में जोड़ते हैं ताकि ui, mandala वग़ैरह मिलें.
    # पूरा package (relative import) बनाने से बचा हूँ — इससे यह app
    # हर तरीक़े से चलती है: python app, python app/__main__.py, दोनों.
    if app_folder not in sys.path:
        sys.path.insert(0, app_folder)

    # Tkinter की जाँच अलग से, क्योंकि कुछ Linux distro में यह अलग से
    # install करना पड़ता है (python3-tk). Windows में हमेशा साथ आता है.
    try:
        import tkinter                                   # noqa: F401
    except ImportError:
        print("Tkinter नहीं मिला.")
        print("Ubuntu/Debian पर यह चलाओ:  sudo apt install python3-tk")
        sys.exit(1)

    from ui import AbhyasApp

    try:
        app = AbhyasApp(jad)
        app.chalao()
    except Exception as e:
        # यहाँ पहुँचे मतलब कुछ ऐसा टूटा जिसकी हमने उम्मीद नहीं की थी.
        # बच्चे को हिंदी में बताओ, और पूरा ब्योरा file में लिख दो ताकि
        # बाद में देखा जा सके.
        import traceback

        vivaran = traceback.format_exc()
        try:
            log = os.path.join(jad, "mera-kaam", "gadbad.txt")
            with open(log, "w", encoding="utf-8") as f:
                f.write(vivaran)
        except (IOError, OSError):
            log = "(लिखा नहीं जा सका)"

        print("अभ्यास खुल नहीं पाया.")
        print("यह तुम्हारी ग़लती नहीं है — app में कुछ गड़बड़ है.")
        print("\nपूरा ब्योरा यहाँ लिखा है:", log)
        print("वो file अपने शिक्षक को दिखा दो.\n")
        print("संक्षेप में:", type(e).__name__, "-", str(e))

        # खिड़की तुरंत बंद न हो, ताकि बच्चा संदेश पढ़ सके.
        # Windows पर .bat से चलाने पर यह सबसे ज़रूरी है.
        try:
            input("\nबंद करने के लिए Enter दबाओ…")
        except (EOFError, KeyboardInterrupt):
            pass
        sys.exit(1)


if __name__ == "__main__":
    mukhya()
