#!/usr/bin/env bash
# ===================================================================
#  अभ्यास (ABHYAS) — Linux पर चलाने वाली file
#
#  चलाओ:  ./start.sh
#  पहली बार:  chmod +x start.sh
#
#  यह तुम्हारे अपने Ubuntu के लिए है, और उन college labs के लिए
#  जहाँ Linux चलता है. बच्चों के Windows वाले laptop पर START.bat जाता है.
# ===================================================================

# इस script का अपना folder — चाहे कहीं से चलाया जाए, रास्ता सही रहे
cd "$(dirname "$0")" || exit 1

# साथ आया हुआ python पहले, फिर मशीन का
if [ -x "python/bin/python3" ]; then
    PY="python/bin/python3"
elif command -v python3 >/dev/null 2>&1; then
    PY="python3"
else
    echo ""
    echo "  Python नहीं मिला."
    echo "  Ubuntu पर चलाओ:  sudo apt install python3 python3-tk"
    echo ""
    exit 1
fi

# Tkinter अलग से जाँचते हैं, क्योंकि Ubuntu में python3 तो होता है
# पर python3-tk अक्सर नहीं होता — और तब error उलझाने वाला आता है
if ! "$PY" -c "import tkinter" >/dev/null 2>&1; then
    echo ""
    echo "  Tkinter नहीं मिला (python3 है, पर tkinter नहीं)."
    echo "  चलाओ:  sudo apt install python3-tk"
    echo ""
    exit 1
fi

exec "$PY" app
