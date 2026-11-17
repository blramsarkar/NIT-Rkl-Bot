import os
import subprocess
import base64
import pypdf
import os
REPORT_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. First, read the base64 of the images to embed in HTML directly
def get_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

logo_b64 = get_base64(os.path.join(REPORT_DIR, "Im1.png"))
fig31_b64 = get_base64(os.path.join(REPORT_DIR, "figure_3_1_pipeline.png"))
fig41_b64 = get_base64(os.path.join(REPORT_DIR, "figure_4_1_results.png"))

print("Images encoded successfully.")
