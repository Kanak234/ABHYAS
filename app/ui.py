# -*- coding: utf-8 -*-
"""
परदा (UI) — ABHYAS की खिड़की.

यह क्या है:
    तीन हिस्सों वाली एक खिड़की —
        बाएँ : आज का पाठ (पढ़ने के लिए)
        दाएँ : code लिखने की जगह
        नीचे : चलाओ / जाँचो के बाद जो आया

यह ऐसा क्यों — Tkinter क्यों, कुछ बढ़िया क्यों नहीं:
    Tkinter Python के साथ ही आता है. कुछ install नहीं करना.
    यही एक बात इसे हर दूसरे विकल्प से बेहतर बनाती है, क्योंकि हमारा
    निशाना वो laptop है जिस पर Windows 7 है, 4 GB RAM है, और admin
    का password बच्चे के पास नहीं है.

    PyQt सुंदर होता, पर 60 MB का होता और उसे install करना पड़ता.
    Electron की तो बात ही छोड़ो. सुंदरता की क़ीमत यहाँ बहुत ज़्यादा है.

यह कहाँ जुड़ता है:
    paath.py  से पाठ लेता है
    parikshak.py से code चलवाता है
    nidan.py से निदान लेता है
    mandala.py में प्रगति लिखता है
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox, scrolledtext

from mandala import Mandala, VALAYA_2, VALAYA_3
from nidan import Nidan
from paath import PaathSangrah
from parikshak import Parikshak

# रंग एक ही जगह. बदलना हो तो यहीं बदलो.
# गहरे रंग जान-बूझकर नहीं चुने — पुराने laptop की screen अक्सर फीकी होती है
# और उस पर गहरा background पढ़ने में तकलीफ़ देता है.
RANG = {
    "pusht": "#faf8f4",        # पृष्ठभूमि — हल्की गर्म, आँख को आराम
    "patti": "#2d2a26",        # ऊपर की पट्टी
    "patti_akshar": "#f5f1ea",
    "code_pusht": "#ffffff",
    "safal": "#1a7a3e",
    "asafal": "#a63d2f",
    "sanket": "#7a5c1e",
    "halka": "#6b6660",
}


class AbhyasApp(object):
    """पूरी app एक ही object में. सादा रखा है ताकि पढ़ने में आसान रहे."""

    def __init__(self, jad):
        """jad = ABHYAS folder का रास्ता (जिसमें app, paath, mandala सब हैं)."""
        self.jad = jad

        # चारों हिस्से जोड़ते हैं
        self.mandala = Mandala(os.path.join(jad, "mandala"))
        self.sangrah = PaathSangrah(os.path.join(jad, "paath"))
        self.nidan = Nidan(os.path.join(jad, "nidan", "niyam.json"))
        self.parikshak = Parikshak()

        self.kaam_ki_jagah = os.path.join(jad, "mera-kaam")
        os.makedirs(self.kaam_ki_jagah, exist_ok=True)

        # app खुलते ही पुरानी चीज़ें साफ़ — कोई background thread नहीं,
        # क्योंकि कमज़ोर मशीन पर हर चालू thread की क़ीमत है
        self.mandala.safai()

        self.abhi_paath = None
        self._khidki_banao()
        self._paath_kholo(self.sangrah.agla(self.mandala))

    # -- खिड़की बनाना --------------------------------------------------------

    def _khidki_banao(self):
        self.khidki = tk.Tk()
        self.khidki.title("अभ्यास — ABHYAS")
        self.khidki.configure(bg=RANG["pusht"])

        # 1024x600 चुना है क्योंकि पुराने laptop अक्सर 1366x768 पर होते हैं,
        # और उससे बड़ी खिड़की परदे से बाहर चली जाती है
        self.khidki.geometry("1024x640")
        self.khidki.minsize(800, 500)

        # हिंदी के लिए ऐसा font चुनना है जो Windows 7 पर भी मौजूद हो.
        # पहले जो मिले वही ले लेते हैं — बिना जाँचे कोई नाम लिख देना
        # सबसे आम गलती है, और तब देवनागरी डिब्बों में बदल जाती है.
        self.paath_font = self._font_chuno(
            ["Nirmala UI", "Mangal", "Noto Sans Devanagari", "Lohit Devanagari"],
            11)
        self.code_font = self._font_chuno(
            ["Consolas", "DejaVu Sans Mono", "Courier New"], 11)

        self._patti_banao()

        # मुख्य हिस्सा — बाएँ पाठ, दाएँ code
        beech = tk.PanedWindow(self.khidki, orient=tk.HORIZONTAL,
                               bg=RANG["pusht"], sashwidth=6, bd=0)
        beech.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 4))

        # बायाँ: पाठ
        baayan = tk.Frame(beech, bg=RANG["pusht"])
        self.paath_box = scrolledtext.ScrolledText(
            baayan, wrap=tk.WORD, font=self.paath_font,
            bg=RANG["pusht"], relief=tk.FLAT, padx=14, pady=10,
            spacing1=2, spacing3=6)
        self.paath_box.pack(fill=tk.BOTH, expand=True)
        self.paath_box.config(state=tk.DISABLED)
        beech.add(baayan, minsize=280, width=420)

        # दायाँ: code + नतीजा
        dayan = tk.Frame(beech, bg=RANG["pusht"])

        self.code_box = scrolledtext.ScrolledText(
            dayan, wrap=tk.NONE, font=self.code_font,
            bg=RANG["code_pusht"], relief=tk.SOLID, bd=1,
            padx=8, pady=6, undo=True)          # undo=True -> Ctrl+Z चलेगा
        self.code_box.pack(fill=tk.BOTH, expand=True)

        self._button_patti(dayan)

        self.natija_box = scrolledtext.ScrolledText(
            dayan, wrap=tk.WORD, font=self.paath_font, height=11,
            bg=RANG["pusht"], relief=tk.SOLID, bd=1, padx=10, pady=8)
        self.natija_box.pack(fill=tk.BOTH, pady=(4, 0))
        self.natija_box.config(state=tk.DISABLED)

        # नतीजे में रंग लगाने के लिए tags
        self.natija_box.tag_config("safal", foreground=RANG["safal"])
        self.natija_box.tag_config("asafal", foreground=RANG["asafal"])
        self.natija_box.tag_config("sanket", foreground=RANG["sanket"])
        self.natija_box.tag_config("halka", foreground=RANG["halka"])
        self.natija_box.tag_config("mota", font=(self.paath_font[0], 11, "bold"))

        beech.add(dayan, minsize=380)

        # पाठ वाले box में शीर्षक बड़े दिखें
        self.paath_box.tag_config(
            "sheershak", font=(self.paath_font[0], 14, "bold"), spacing3=8)
        self.paath_box.tag_config(
            "upsheershak", font=(self.paath_font[0], 12, "bold"),
            spacing1=10, spacing3=4)
        self.paath_box.tag_config(
            "code", font=(self.code_font[0], 10), background="#f0ece4")

        # Ctrl+S से बचत, F5 से चलाओ — आदत वाले shortcut
        self.khidki.bind("<Control-s>", lambda e: self._bachao())
        self.khidki.bind("<F5>", lambda e: self._chalao())

    def _font_chuno(self, naam_suchi, aakar):
        """
        दी हुई सूची में से पहला font जो इस मशीन पर मौजूद है.

        यह जाँच ज़रूरी है. Windows 7 पर 'Noto Sans Devanagari' नहीं होता,
        और अगर बिना जाँचे वही लिख दें तो हिंदी डिब्बों में बदल जाएगी —
        और बच्चा पहली ही नज़र में app बंद कर देगा.
        """
        maujood = set(tkfont.families())
        for naam in naam_suchi:
            if naam in maujood:
                return (naam, aakar)
        return ("TkDefaultFont", aakar)

    def _patti_banao(self):
        """ऊपर की पट्टी — पाठ का नाम और प्रगति."""
        patti = tk.Frame(self.khidki, bg=RANG["patti"], height=46)
        patti.pack(fill=tk.X)
        patti.pack_propagate(False)

        self.sheershak_label = tk.Label(
            patti, text="अभ्यास", bg=RANG["patti"], fg=RANG["patti_akshar"],
            font=(self.paath_font[0], 13, "bold"), anchor="w", padx=14)
        self.sheershak_label.pack(side=tk.LEFT, fill=tk.Y)

        self.pragati_label = tk.Label(
            patti, text="", bg=RANG["patti"], fg="#a09a92",
            font=(self.paath_font[0], 10), padx=14)
        self.pragati_label.pack(side=tk.RIGHT, fill=tk.Y)

    def _button_patti(self, maalik):
        """चलाओ / जाँचो / सहेजो वाली पट्टी."""
        patti = tk.Frame(maalik, bg=RANG["pusht"])
        patti.pack(fill=tk.X, pady=(6, 0))

        def button(text, hukum, mukhya=False):
            b = tk.Button(
                patti, text=text, command=hukum,
                font=(self.paath_font[0], 10, "bold" if mukhya else "normal"),
                bg="#2d6a4f" if mukhya else "#e8e3da",
                fg="white" if mukhya else "#2d2a26",
                relief=tk.FLAT, padx=16, pady=6, cursor="hand2",
                activebackground="#245c42" if mukhya else "#dcd6cc")
            b.pack(side=tk.LEFT, padx=(0, 6))
            return b

        button("▶  चलाओ   (F5)", self._chalao)
        button("✓  जाँचो", self._jaancho, mukhya=True)
        button("सहेजो  (Ctrl+S)", self._bachao)
        button("सुराग़", self._suraag)

        self.sthiti = tk.Label(patti, text="", bg=RANG["pusht"],
                               fg=RANG["halka"], font=(self.paath_font[0], 9))
        self.sthiti.pack(side=tk.RIGHT)

    # -- पाठ दिखाना ---------------------------------------------------------

    def _paath_kholo(self, paath):
        """एक पाठ परदे पर लाता है."""
        if paath is None:
            messagebox.showinfo("पूरा हुआ", "सारे पाठ हो गए. शाबाश!")
            return

        self.abhi_paath = paath
        self.sheershak_label.config(text=paath.get("sheershak", paath["id"]))

        kul = len(self.sangrah.sab())
        hue = 0
        for p in self.sangrah.sab():
            pr = self.mandala.padho(VALAYA_2, "pragati", p["id"])
            if pr and pr.get("poora"):
                hue += 1
        self.pragati_label.config(text="%d / %d पाठ पूरे" % (hue, kul))

        self._markdown_dikhao(paath.get("padho", ""))

        # पहले बच्चे का सहेजा हुआ code देखो; न हो तो पाठ का ढाँचा.
        # यह क्रम मायने रखता है — बच्चे का काम कभी नहीं मिटना चाहिए.
        bacha_hua = self._bacha_hua_code(paath["id"])
        self.code_box.delete("1.0", tk.END)
        self.code_box.insert("1.0", bacha_hua or paath.get("shuruaat", ""))
        self.code_box.edit_reset()      # undo का इतिहास यहाँ से शुरू

    def _markdown_dikhao(self, text):
        """
        Markdown को बहुत सादे तरीक़े से दिखाता है.

        पूरा markdown parser नहीं बनाया — सिर्फ़ शीर्षक और code वाली लाइनें.
        जान-बूझकर, क्योंकि पूरा parser 300 लाइन का होता, और पाठ हम ख़ुद
        लिख रहे हैं. जो अपने हाथ में है उसके लिए parser बनाना फ़िज़ूल है.
        """
        self.paath_box.config(state=tk.NORMAL)
        self.paath_box.delete("1.0", tk.END)

        code_me = False
        for line in text.split("\n"):
            if line.strip().startswith("```"):
                code_me = not code_me
                continue
            if code_me or line.startswith("    "):
                self.paath_box.insert(tk.END, line + "\n", "code")
            elif line.startswith("## "):
                self.paath_box.insert(tk.END, line[3:] + "\n", "upsheershak")
            elif line.startswith("# "):
                self.paath_box.insert(tk.END, line[2:] + "\n", "sheershak")
            else:
                self.paath_box.insert(tk.END, line + "\n")

        self.paath_box.config(state=tk.DISABLED)

    # -- बच्चे का code सँभालना ----------------------------------------------

    def _code_file(self, paath_id):
        return os.path.join(self.kaam_ki_jagah, paath_id + ".py")

    def _bacha_hua_code(self, paath_id):
        rasta = self._code_file(paath_id)
        if not os.path.exists(rasta):
            return None
        try:
            with open(rasta, "r", encoding="utf-8") as f:
                return f.read()
        except (IOError, OSError):
            return None

    def _bachao(self):
        """
        बच्चे का code file में सहेजता है.

        mera-kaam/ folder में, यानी pen drive पर ही. इसलिए बच्चा किसी भी
        computer पर pen drive लगाकर वहीं से काम जारी रख सकता है जहाँ छोड़ा था.
        यह इस project की सबसे काम की बात है — क्योंकि जिसके पास laptop नहीं,
        वो college के lab के किसी भी PC पर बैठ सकता है.
        """
        if self.abhi_paath is None:
            return
        code = self.code_box.get("1.0", tk.END)
        try:
            with open(self._code_file(self.abhi_paath["id"]), "w",
                      encoding="utf-8") as f:
                f.write(code)
            self.sthiti.config(text="सहेजा गया")
        except (IOError, OSError) as e:
            self.sthiti.config(text="सहेजा नहीं जा सका: " + str(e))

    # -- चलाओ ---------------------------------------------------------------

    def _chalao(self):
        """code चलाकर output दिखाता है. कोई जाँच नहीं."""
        self._bachao()
        self.sthiti.config(text="चल रहा है…")
        self.khidki.update_idletasks()

        code = self.code_box.get("1.0", tk.END)
        # अलग thread में इसलिए कि 10 सेकंड तक खिड़की जमी हुई न लगे
        threading.Thread(target=self._chalao_thread, args=(code,),
                         daemon=True).start()

    def _chalao_thread(self, code):
        r = self.parikshak.chalao(code, self.kaam_ki_jagah)
        # Tkinter को दूसरे thread से छूना मना है, इसलिए after() से
        # वापस मुख्य thread में जाते हैं
        self.khidki.after(0, lambda: self._chalao_dikhao(r))

    def _chalao_dikhao(self, r):
        self.sthiti.config(text="")
        self._natija_saaf()

        if r["samay_khatam"]:
            self._likho("code दस सेकंड में ख़त्म नहीं हुआ.\n", "asafal", "mota")
            self._likho(
                "लगभग हमेशा इसका मतलब होता है कि कोई loop कभी रुका ही नहीं.\n"
                "अपने while या for को देखो — क्या उसकी शर्त कभी झूठी होगी?\n",
                "halka")
        elif r["error"]:
            self._likho("गड़बड़:\n", "asafal", "mota")
            self._likho(r["error"] + "\n")
            self._nidan_dikhao({"code": self.code_box.get("1.0", tk.END),
                                "error": r["error"], "stdout": r["stdout"],
                                "natija": {}, "paath_id": self.abhi_paath["id"]})
        else:
            self._likho("output:\n", "halka")
            self._likho(r["stdout"] or "(कुछ छपा नहीं — print() लगाकर देखो)\n")

    # -- जाँचो ---------------------------------------------------------------

    def _jaancho(self):
        """code को पाठ के test cases पर परखता है."""
        self._bachao()
        self.sthiti.config(text="जाँच रहा है…")
        self.khidki.update_idletasks()

        code = self.code_box.get("1.0", tk.END)
        threading.Thread(target=self._jaancho_thread, args=(code,),
                         daemon=True).start()

    def _jaancho_thread(self, code):
        r = self.parikshak.jaancho(code, self.abhi_paath, self.kaam_ki_jagah)
        self.khidki.after(0, lambda: self._jaancho_dikhao(code, r))

    def _jaancho_dikhao(self, code, r):
        self.sthiti.config(text="")
        self._natija_saaf()

        # हर कोशिश वलय-3 में दर्ज होती है (7 दिन में अपने आप मिट जाएगी).
        # यही वो कच्चा data है जिससे तुम बाद में देख सकते हो कि बच्चे
        # किस पाठ पर सबसे ज़्यादा अटकते हैं.
        self.mandala.jodo(VALAYA_3, "koshish", self.abhi_paath["id"], {
            "safal": r.get("safal", False),
            "lambai": len(code),
        })

        if r.get("samay_khatam"):
            self._likho("code दस सेकंड में ख़त्म नहीं हुआ — शायद कोई loop रुका नहीं.\n",
                        "asafal", "mota")
            return

        parinam = r.get("jaanch_parinam", [])
        if not parinam:
            self._likho("code चला ही नहीं.\n", "asafal", "mota")
            if r.get("error"):
                self._likho(self._error_chhanto(r["error"]) + "\n")
        else:
            pass_hue = 0
            for j in parinam:
                if j["safal"]:
                    pass_hue += 1
                    self._likho("  ✓  " + j["naam"] + "\n", "safal")
                else:
                    self._likho("  ✗  " + j["naam"] + "\n", "asafal")
                    if j.get("sandesh"):
                        self._likho("       " + j["sandesh"] + "\n", "halka")
                    elif j.get("mila") is not None:
                        self._likho("       मिला: " + str(j["mila"]) + "\n",
                                    "halka")
            self._likho("\n%d में से %d जाँच पास.\n" % (len(parinam), pass_hue),
                        "mota")

        # निदान — यही असली मदद है
        self._nidan_dikhao({
            "code": code,
            "error": r.get("error", ""),
            "stdout": r.get("stdout", ""),
            "natija": r.get("natija", {}),
            "paath_id": self.abhi_paath["id"],
        })

        # पूरा हुआ तो प्रगति वलय-2 में चढ़ा दो (यानी स्थायी हो जाए)
        if r.get("safal"):
            self.mandala.likho(VALAYA_2, "pragati", self.abhi_paath["id"],
                               {"poora": True})
            self._likho("\nपाठ पूरा हुआ. शाबाश.\n", "safal", "mota")
            self._paath_kholo_dobara()

    def _error_chhanto(self, error):
        """
        Error text में से ABHYAS की अपनी files की लाइनें हटाता है.

        बिना इसके बच्चे को _chalak.py और importlib की लाइनें दिखतीं, जिनसे
        उसका कोई लेना-देना नहीं. वो उन्हीं में उलझ जाता. सिर्फ़ उसकी अपनी
        ग़लती दिखनी चाहिए.
        """
        rakhne_layak = []
        for line in error.split("\n"):
            if "_chalak.py" in line or "importlib" in line:
                continue
            if "frozen importlib" in line:
                continue
            rakhne_layak.append(line)
        return "\n".join(rakhne_layak).strip()

    def _nidan_dikhao(self, sandarbh):
        """निदान engine से पूछकर हिंदी में समझाता है."""
        mile = self.nidan.jaancho(sandarbh)
        if not mile:
            return
        self._likho("\n" + "─" * 46 + "\n", "halka")
        for n in mile:
            if not n["sheershak"]:
                continue
            self._likho("\n" + n["sheershak"] + "\n", "sanket", "mota")
            self._likho(n["vyakhya"] + "\n")
            if n["sanket"]:
                self._likho("→ " + n["sanket"] + "\n", "sanket")

    def _paath_kholo_dobara(self):
        """पाठ पूरा होने पर पूछता है कि अगला खोलें या नहीं."""
        agla = self.sangrah.agla(self.mandala)
        if agla is None:
            return
        if messagebox.askyesno("अगला पाठ",
                               "अगला पाठ खोलें?\n\n" + agla.get("sheershak", "")):
            self._paath_kholo(agla)

    # -- सुराग़ ---------------------------------------------------------------

    def _suraag(self):
        """
        पाठ के सुराग़ एक-एक करके दिखाता है.

        सारे एक साथ नहीं — क्योंकि तब बच्चा सोचना छोड़कर सीधे जवाब पढ़ लेगा.
        एक-एक करके देने से वो हर सुराग़ के बाद ख़ुद कोशिश करता है.
        गिनती वलय-3 में रहती है, यानी अगले हफ़्ते फिर शून्य से शुरू.
        """
        if self.abhi_paath is None:
            return
        suraag = self.abhi_paath.get("sanket_kram", [])
        if not suraag:
            self._natija_saaf()
            self._likho("इस पाठ में कोई सुराग़ नहीं है.\n", "halka")
            return

        rec = self.mandala.padho(VALAYA_3, "suraag", self.abhi_paath["id"])
        ginti = (rec or {}).get("ginti", 0)

        self._natija_saaf()
        if ginti >= len(suraag):
            self._likho("सारे सुराग़ दिखा चुके.\n\n", "halka")
            for i, s in enumerate(suraag):
                self._likho("%d. %s\n" % (i + 1, s), "sanket")
            return

        self._likho("सुराग़ %d:\n" % (ginti + 1), "sanket", "mota")
        self._likho(suraag[ginti] + "\n\n")
        self._likho("पहले ख़ुद कोशिश करो. फिर भी न बने तो दोबारा दबाओ.\n",
                    "halka")
        self.mandala.likho(VALAYA_3, "suraag", self.abhi_paath["id"],
                           {"ginti": ginti + 1})

    # -- नतीजा box के छोटे सहायक ---------------------------------------------

    def _natija_saaf(self):
        self.natija_box.config(state=tk.NORMAL)
        self.natija_box.delete("1.0", tk.END)
        self.natija_box.config(state=tk.DISABLED)

    def _likho(self, text, *tags):
        self.natija_box.config(state=tk.NORMAL)
        self.natija_box.insert(tk.END, text, tags)
        self.natija_box.see(tk.END)
        self.natija_box.config(state=tk.DISABLED)

    # -- चलाओ ---------------------------------------------------------------

    def chalao(self):
        self.khidki.mainloop()
