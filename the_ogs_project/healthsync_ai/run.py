import os
import sys

# Ensure healthsync_ai root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("                 HEALTHSYNC AI")
    print("         National Health Command Center")
    print("=" * 60)
    print(" * Running on http://127.0.0.1:5000")
    print(" * Demo Login: admin@healthsync.gov | admin2026")
    print("=" * 60)
    app.run(debug=True, host='127.0.0.1', port=5000)
