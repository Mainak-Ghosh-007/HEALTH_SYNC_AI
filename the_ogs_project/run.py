import os
import sys

# Ensure healthsync_ai is in the path
root_dir = os.path.dirname(os.path.abspath(__file__))
sub_dir = os.path.join(root_dir, 'healthsync_ai')
if sub_dir not in sys.path:
    sys.path.insert(0, sub_dir)

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
