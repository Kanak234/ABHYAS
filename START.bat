@echo off
REM ===================================================================
REM  अभ्यास (ABHYAS) — Windows पर चलाने वाली file
REM
REM  इसे बस दो बार click करो. और कुछ नहीं करना.
REM
REM  यह file क्या करती है:
REM    1. पहले साथ आए हुए python folder में देखती है (pen drive वाला)
REM    2. न मिले तो मशीन में लगे python को आज़माती है
REM    3. दोनों न हों तो हिंदी में बताती है कि क्या करना है
REM
REM  पहला क्रम जान-बूझकर है: pen drive वाला python हमेशा जीते,
REM  क्योंकि मशीन में लगा python पुराना या टूटा हो सकता है, और
REM  हमें हर मशीन पर एक जैसा बर्ताव चाहिए.
REM ===================================================================

chcp 65001 >nul 2>&1
REM ऊपर वाली लाइन Windows की कमांड-खिड़की को UTF-8 पर लाती है.
REM इसके बिना हिंदी के अक्षर कूड़े जैसे दिखते हैं.

title अभ्यास - ABHYAS
cd /d "%~dp0"
REM %~dp0 = इस .bat file का अपना folder. इससे pen drive किसी भी
REM drive letter (E:, F:, G:) पर लगे, app को फ़र्क़ नहीं पड़ता.

REM --- 1. साथ आया हुआ python ---
if exist "python\python.exe" (
    echo अभ्यास खुल रहा है...
    "python\python.exe" app
    goto :khatam
)

REM --- 2. मशीन का python ---
where python >nul 2>&1
if %errorlevel%==0 (
    echo अभ्यास खुल रहा है...
    python app
    goto :khatam
)

REM --- 3. कहीं नहीं मिला ---
echo.
echo   =========================================
echo    Python इस computer पर नहीं मिला
echo   =========================================
echo.
echo   अभ्यास चलाने के लिए Python चाहिए.
echo.
echo   अगर तुम्हें pen drive मिली थी, तो उसमें
echo   'python' नाम का folder होना चाहिए था.
echo   शायद copy करते वक़्त वो छूट गया.
echo   पूरा folder दोबारा copy करो.
echo.
echo   अगर तुम ख़ुद setup कर रहे हो, तो
echo   PADHO.txt पढ़ो - उसमें पूरा तरीक़ा लिखा है.
echo.
pause
goto :eof

:khatam
REM app बंद होने पर खिड़की तुरंत ग़ायब न हो, ताकि कोई संदेश हो तो पढ़ा जा सके
if %errorlevel% neq 0 pause
