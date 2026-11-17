"""
==============================================================================
NIT Rourkela Chatbot Launcher
Run from project root: python run.py
==============================================================================
"""

import sys
import os
import uvicorn

# Ensure backend directory is in sys.path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

if __name__ == "__main__":
    print("=" * 65)
    print(" Starting NIT RKL Bot Server & Web Portal...")
    print(" Web Portal & Chatbot: http://localhost:8000/")
    print(" API Documentation:    http://localhost:8000/docs")
    print("=" * 65)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

