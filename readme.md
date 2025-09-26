Financial Chatbot — Prototype
--------------------------------
Run:
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  python app.py
  Open http://localhost:5000

Files:
  - data/financials.csv    : sample financial dataset
  - chatbot/core.py        : chatbot logic
  - app.py                 : Flask app
  - templates/index.html   : UI
  - static/js/chat.js      : frontend logic
  - static/plots/          : generated plots
  - tests/                 : pytest test suite

Notes:
  - This is a rule-based prototype. Add spaCy or an LLM for better NLU.
  - To produce plots, the dataset must contain numeric values and year column.
