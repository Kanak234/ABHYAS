# -*- coding: utf-8 -*-
"""
pen_drive_banao.py — बच्चों के लिए pen drive वाला package बनाने का script.

यह किसके लिए है:
    सिर्फ़ तुम्हारे लिए, कनक. बच्चा इसे कभी नहीं चलाएगा.

यह क्या करता है:
    ABHYAS folder को इस तरह तैयार करता है कि वो Windows 7 वाले किसी भी
    laptop पर बिना कुछ install किए चल जाए.

क्यों ज़रूरी है:
    बच्चे की मशीन पर python नहीं है, और वो install भी नहीं कर सकता
    (admin का password नहीं होता, ख़ासकर college lab में). इसलिए python
    को साथ ले जाना पड़ेगा — pen drive में, folder की शक्ल में.

चलाओ:
    python3 tools/pen_drive_banao.py

------------------------------------------------------------------------
पूरा तरीक़ा — एक बार करना है, फिर हमेशा के लिए
------------------------------------------------------------------------

क़दम 1 — python उतारो (यह तुम्हें एक बार हाथ से करना है)

    Windows 7 के लिए आख़िरी काम का python 3.8.10 है. उससे नया कोई
    version Windows 7 पर चलता ही नहीं — यह पक्की सीमा है, इसमें
    कोई तरकीब नहीं चलती.

    python.org से यह file उतारो (कहीं भी internet वाली मशीन पर):
        python-3.8.10-embed-amd64.zip
    पुराने 32-bit laptop के लिए:
        python-3.8.10-embed-win32.zip

    "embeddable" वाला ही लेना है, installer वाला नहीं. वो लगभग 15 MB का
    है, और उसे install नहीं करना पड़ता — बस खोलकर रख दो, चल जाता है.
    यही हमें चाहिए.

क़दम 2 — उसे ABHYAS/python/ में खोलो

    ABHYAS/
      python/
        python.exe
        python38.zip
        python38._pth      <- इसे बदलना है, क़दम 3 देखो

क़दम 3 — python38._pth में एक लाइन जोड़ो

    उस file को notepad में खोलो. आख़िर में यह लाइन जोड़ो:

        import site

    यह ज़रूरी क्यों: embeddable python default में बाहरी packages
    (numpy वग़ैरह) ढूँढता ही नहीं. यह एक लाइन उसे ढूँढना सिखाती है.
    इसके बिना numpy install तो हो जाएगा पर import नहीं होगा, और
    तुम घंटों उलझोगे कि "install तो किया था".

क़दम 4 — packages डालो (internet वाली मशीन पर, एक बार)

    इस script को चलाओ, वो पूरा हुक्म छापकर दे देगा.

क़दम 5 — जाँचो

    उस pen drive को किसी दूसरी मशीन पर लगाकर START.bat चलाओ.
    अपनी मशीन पर जाँचना काफ़ी नहीं — तुम्हारी मशीन पर बहुत कुछ पहले से
    लगा है जो बच्चे की मशीन पर नहीं होगा.
------------------------------------------------------------------------
"""

import os
import shutil
import sys

# ---------------------------------------------------------------------------
# जो packages चाहिए, version के साथ पक्के किए हुए.
#
# Version यहाँ जान-बूझकर जमाए हैं. वजह: दो साल बाद pip उठाकर नया version
# लाएगा, और वो Python 3.8 पर चलेगा ही नहीं (numpy 1.25 से आगे 3.9+ माँगता है).
# तब पूरा package टूट जाएगा और तुम्हें पता भी नहीं चलेगा — जब तक कोई बच्चा
# न बताए.
#
# ये सारे 3.8 पर चलने वाले आख़िरी version हैं.
# ---------------------------------------------------------------------------
PACKAGES = [
    "numpy==1.24.4",         # 3.8 पर चलने वाला आख़िरी numpy
    "pandas==2.0.3",         # 3.8 पर चलने वाला आख़िरी pandas
    "scikit-learn==1.3.2",   # 3.8 पर चलने वाला आख़िरी sklearn
    "matplotlib==3.7.5",     # 3.8 पर चलने वाला आख़िरी matplotlib
]

# जो चीज़ें pen drive पर नहीं जानी चाहिए
CHHODO = {
    "__pycache__", ".git", ".gitignore", "tools",
    "mera-kaam", ".pytest_cache",
}

# जिन files के नाम ये हों, वो भी नहीं जाएँगी.
#
# hal.py सबसे ज़रूरी है — वो हर पाठ का सही जवाब है, जो तुम्हारे पास
# जाँच के लिए रहता है (sab_jaancho.py उसी को चलाकर पक्का करता है कि
# पाठ की जाँच सही है). पर अगर वो बच्चे तक पहुँच गया, तो वो सोचना छोड़कर
# सीधा जवाब देख लेगा — और पूरा project बेकार.
FILE_CHHODO = {"hal.py"}


def hukum_chhapo():
    """package उतारने का पूरा हुक्म छापता है."""
    print("=" * 70)
    print("  क़दम 4 — packages उतारना")
    print("=" * 70)
    print()
    print("  यह हुक्म internet वाली किसी भी मशीन पर चलाओ.")
    print("  ज़रूरी नहीं कि वो Windows हो — Linux से भी Windows के")
    print("  packages उतारे जा सकते हैं. --platform वाला हिस्सा यही करता है.")
    print()
    print("  64-bit laptop के लिए:")
    print()
    print("    pip download --only-binary=:all: \\")
    print("      --platform win_amd64 --python-version 38 \\")
    print("      -d wheels \\")
    for p in PACKAGES:
        print("      " + p + " \\")
    print()
    print("  32-bit के लिए: win_amd64 की जगह win32 लिखो.")
    print()
    print("  फिर उन wheels को pen drive वाले python में डालो:")
    print()
    print("    python\\python.exe -m pip install --no-index \\")
    print("      --find-links wheels numpy pandas scikit-learn matplotlib")
    print()
    print("  (embeddable python में pip नहीं आता. पहले get-pip.py")
    print("   उतारकर  python\\python.exe get-pip.py  चलाना पड़ेगा.)")
    print()


def naap_lo(jad):
    """package कितना बड़ा होगा, इसका अंदाज़ा."""
    kul = 0
    ginti = 0
    for dirpath, dirnames, filenames in os.walk(jad):
        dirnames[:] = [d for d in dirnames if d not in CHHODO]
        for f in filenames:
            try:
                kul += os.path.getsize(os.path.join(dirpath, f))
                ginti += 1
            except OSError:
                pass
    return kul, ginti


def jaancho(jad):
    """
    package भेजने से पहले की जाँच सूची.

    यह इसलिए है कि तुम कोई ज़रूरी चीज़ छोड़कर 50 pen drive न बाँट दो.
    """
    print("=" * 70)
    print("  जाँच सूची")
    print("=" * 70)
    print()

    zaroori = [
        ("START.bat", "Windows वाली launcher"),
        ("start.sh", "Linux वाली launcher"),
        ("app/__main__.py", "app की शुरुआत"),
        ("app/ui.py", "खिड़की"),
        ("app/mandala.py", "data store"),
        ("app/nidan.py", "निदान engine"),
        ("app/parikshak.py", "code चलाने वाला"),
        ("app/paath.py", "पाठ पढ़ने वाला"),
        ("nidan/niyam.json", "नियमों की किताब"),
        ("PADHO.txt", "बच्चे के लिए निर्देश"),
    ]

    sab_theek = True
    for rasta, kya in zaroori:
        poora = os.path.join(jad, rasta)
        if os.path.exists(poora):
            print("  [ ठीक ] %-24s %s" % (rasta, kya))
        else:
            print("  [ नहीं ] %-24s %s   <<< छूट गया" % (rasta, kya))
            sab_theek = False

    # पाठ गिनो
    paath_folder = os.path.join(jad, "paath")
    paath_ginti = 0
    if os.path.isdir(paath_folder):
        for d in os.listdir(paath_folder):
            if os.path.exists(os.path.join(paath_folder, d, "paath.json")):
                paath_ginti += 1
    print()
    print("  पाठ मिले: %d" % paath_ginti)
    if paath_ginti == 0:
        print("  <<< एक भी पाठ नहीं! बच्चा app खोलेगा और ख़ाली मिलेगी.")
        sab_theek = False

    # python साथ है या नहीं
    print()
    if os.path.exists(os.path.join(jad, "python", "python.exe")):
        print("  [ ठीक ] python/ folder साथ है — Windows पर चलेगा")
    else:
        print("  [ ध्यान ] python/ folder नहीं है.")
        print("           अपनी मशीन पर तो चलेगा, पर बच्चे की मशीन पर नहीं.")
        print("           ऊपर लिखे क़दम 1-3 पहले करो.")

    kul, ginti = naap_lo(jad)
    print()
    print("  नाप: %.1f MB, %d files" % (kul / (1024.0 * 1024.0), ginti))
    if kul > 500 * 1024 * 1024:
        print("  <<< 500 MB से ऊपर. Pen drive पर copy होने में देर लगेगी.")

    print()
    return sab_theek


def zip_banao(jad):
    """पूरे folder की एक zip बनाता है, बाँटने के लिए."""
    bahar = os.path.join(os.path.dirname(jad), "ABHYAS-baantne-ke-liye")
    print("  zip बन रही है… (थोड़ा समय लगेगा)")

    def chhodo(folder, naam_suchi):
        return [n for n in naam_suchi
                if n in CHHODO or n in FILE_CHHODO]

    asthayi = bahar + "-tmp"
    if os.path.exists(asthayi):
        shutil.rmtree(asthayi)
    shutil.copytree(jad, asthayi, ignore=chhodo)

    # ख़ाली mera-kaam रखते हैं ताकि बच्चे की app पहली बार में ही चल जाए
    os.makedirs(os.path.join(asthayi, "mera-kaam"), exist_ok=True)

    zip_rasta = shutil.make_archive(bahar, "zip", asthayi)
    shutil.rmtree(asthayi)

    # आख़िरी सुरक्षा: zip में कोई hal.py तो नहीं रह गई?
    # ऊपर वाली छँटाई पहले ही कर चुकी है, पर यह जाँच इसलिए रखी है कि
    # यह वो ग़लती है जिसका पता तब चलेगा जब 50 pen drive बँट चुकी होंगी.
    # ऐसी ग़लतियों पर दोहरी जाँच सस्ती है.
    import zipfile
    with zipfile.ZipFile(zip_rasta) as z:
        rah_gayi = [n for n in z.namelist()
                    if os.path.basename(n) in FILE_CHHODO]
    if rah_gayi:
        print()
        print("  >>> ख़तरा: सही हल वाली files package में रह गईं:")
        for r in rah_gayi:
            print("      " + r)
        print("  >>> यह zip मत बाँटो.")
        return None

    naap = os.path.getsize(zip_rasta) / (1024.0 * 1024.0)
    print("  बन गई: %s  (%.1f MB)" % (zip_rasta, naap))
    print("  जाँचा: सही हल वाली कोई file अंदर नहीं गई.")
    return zip_rasta


if __name__ == "__main__":
    yahan = os.path.dirname(os.path.abspath(__file__))
    jad = os.path.dirname(yahan)

    print()
    print("  अभ्यास — pen drive बनाने वाला script")
    print("  folder:", jad)
    print()

    theek = jaancho(jad)

    if "--zip" in sys.argv:
        if theek:
            zip_banao(jad)
        else:
            print("  पहले ऊपर वाली कमियाँ ठीक करो, फिर zip बनाओ.")
    else:
        hukum_chhapo()
        print("  zip बनानी हो तो:  python3 tools/pen_drive_banao.py --zip")
        print()
