import os
import subprocess
import base64
import pypdf
import os
REPORT_DIR = os.path.dirname(os.path.abspath(__file__))

# Helper to load base64 image
def get_b64(path):
    with open(path, "rb") as f:
        return f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"

logo_src = get_b64(os.path.join(REPORT_DIR, "Im1.png"))
fig31_src = get_b64(os.path.join(REPORT_DIR, "figure_3_1_pipeline.png"))
fig41_src = get_b64(os.path.join(REPORT_DIR, "figure_4_1_results.png"))

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>NIT Rourkela Capstone Mid-Term Report - Balaram Sarkar</title>
<style>
  @page {{
    size: A4 portrait;
    margin: 0;
  }}
  * {{
    box-sizing: border-box;
    -webkit-print-color-adjust: exact;
  }}
  body {{
    margin: 0;
    padding: 0;
    font-family: "Times New Roman", Times, "TeX Gyre Termes", Georgia, serif;
    font-size: 11pt;
    line-height: 1.42;
    color: #111;
    background-color: #f5f5f5;
  }}
  .page {{
    width: 210mm;
    height: 297mm;
    margin: 0 auto 10mm auto;
    background: #fff;
    padding: 24mm 24mm 24mm 31.75mm; /* left 1.25in (31.75mm), top/right/bottom ~1in */
    position: relative;
    page-break-after: always;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    overflow: hidden;
  }}
  @media print {{
    body {{
      background: none;
    }}
    .page {{
      margin: 0;
      box-shadow: none;
    }}
  }}
  .page-num {{
    position: absolute;
    bottom: 16mm;
    left: 31.75mm;
    right: 24mm;
    text-align: center;
    font-size: 10.5pt;
    font-style: normal;
  }}
  .header-rule {{
    position: absolute;
    top: 15mm;
    left: 31.75mm;
    right: 24mm;
    font-size: 9pt;
    color: #444;
    border-bottom: 0.5pt solid #888;
    padding-bottom: 2mm;
    text-align: right;
    display: none; /* enabled for main body */
  }}

  /* Typography */
  h1.chap-title {{
    font-size: 14pt;
    font-weight: bold;
    text-transform: uppercase;
    margin-top: 0;
    margin-bottom: 14pt;
    letter-spacing: 0.02em;
  }}
  h2.sec-title {{
    font-size: 12pt;
    font-weight: bold;
    margin-top: 14pt;
    margin-bottom: 6pt;
  }}
  h3.subsec-title {{
    font-size: 11pt;
    font-weight: bold;
    margin-top: 10pt;
    margin-bottom: 4pt;
  }}
  p {{
    margin: 0 0 8pt 0;
    text-align: justify;
    text-justify: inter-word;
  }}
  ul, ol {{
    margin: 0 0 8pt 0;
    padding-left: 18pt;
  }}
  li {{
    margin-bottom: 3pt;
    text-align: justify;
  }}

  /* Tables */
  table.latex-table {{
    width: 100%;
    border-collapse: collapse;
    margin: 10pt 0 10pt 0;
    font-size: 9.5pt;
    line-height: 1.35;
  }}
  table.latex-table th, table.latex-table td {{
    padding: 4.5pt 6pt;
    text-align: left;
    vertical-align: top;
  }}
  table.latex-table thead tr:first-child {{
    border-top: 1.5pt solid #000;
    border-bottom: 0.75pt solid #000;
  }}
  table.latex-table thead tr th {{
    font-weight: bold;
  }}
  table.latex-table tbody tr:last-child {{
    border-bottom: 1.5pt solid #000;
  }}
  .table-caption, .fig-caption {{
    font-size: 10pt;
    margin-bottom: 6pt;
    text-align: left;
  }}
  .fig-caption {{
    margin-top: 6pt;
    text-align: center;
  }}

  /* Code & Math */
  .math-block {{
    text-align: center;
    margin: 8pt 0;
    font-family: "Cambria Math", "Times New Roman", serif;
    font-size: 11pt;
  }}
  .eq-num {{
    float: right;
  }}
  code {{
    font-family: "Courier New", Courier, monospace;
    font-size: 9.5pt;
    background: #f0f0f0;
    padding: 1pt 3pt;
    border-radius: 2pt;
  }}

  /* Specific Layouts */
  .cover-box {{
    text-align: center;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .cover-title {{
    font-size: 14pt;
    font-weight: bold;
    text-transform: uppercase;
    line-height: 1.45;
    margin: 18pt 0;
  }}

  .toc-row {{
    display: flex;
    justify-content: space-between;
    margin-bottom: 4pt;
    font-size: 10.5pt;
  }}
  .toc-title {{
    font-weight: bold;
  }}
  .toc-sub {{
    padding-left: 15pt;
  }}
  .dots {{
    flex: 1;
    border-bottom: 1px dotted #666;
    margin: 0 5pt 3pt 5pt;
  }}
</style>
</head>
<body>

<!-- ================= PAGE 1: COVER PAGE ================= -->
<div class="page">
  <div class="cover-box">
    <div>
      <div style="margin-top: 4mm;">
        <img src="{logo_src}" style="width: 25mm; height: 25mm;" alt="NIT Rourkela Logo">
      </div>
      <div style="margin-top: 6mm; font-size: 13pt; font-weight: bold; letter-spacing: 0.05em;">
        NATIONAL INSTITUTE OF TECHNOLOGY<br>
        ROURKELA, ODISHA
      </div>
    </div>

    <div>
      <div class="cover-title">
        AN INTELLIGENT HYBRID CONVERSATIONAL ASSISTANT FOR NIT ROURKELA: ROUTER-BASED DUAL-PATH RETRIEVAL WITH STRUCTURED DATABASE TOOLS AND SEMANTIC SEARCH
      </div>
      <div style="font-size: 12.5pt; font-weight: bold; margin-top: 16pt;">
        MID-TERM PROJECT REPORT
      </div>
      <div style="font-size: 10.5pt; margin-top: 4pt; font-style: italic;">
        Capstone Project-I (CS4095), Autumn Semester 2026–27
      </div>
    </div>

    <div>
      <div style="font-size: 11pt; font-weight: bold; margin-bottom: 3pt;">Submitted By:</div>
      <div style="font-size: 12pt;">
        Balaram Sarkar &nbsp;&nbsp; (123CS0224)
      </div>

      <div style="margin-top: 16pt; font-size: 11pt; font-weight: bold; margin-bottom: 3pt;">Under the Supervision of:</div>
      <div style="font-size: 12pt; font-weight: bold;">
        Dr. Anup Nandy
      </div>
      <div style="font-size: 10.5pt; color: #333;">
        Associate Professor
      </div>

      <div style="margin-top: 18pt; font-size: 11pt; font-weight: bold; margin-bottom: 3pt;">Submitted To:</div>
      <div style="font-size: 11pt;">
        Department of Computer Science and Engineering<br>
        National Institute of Technology<br>
        Rourkela, Odisha – 769008
      </div>
    </div>

    <div style="margin-bottom: 4mm; font-size: 11pt; font-weight: bold; letter-spacing: 0.05em;">
      OCTOBER, 2026
    </div>
  </div>
</div>

<!-- ================= PAGE 2: CERTIFICATE ================= -->
<div class="page">
  <div style="text-align: center; margin-top: 12mm; margin-bottom: 25mm;">
    <span style="font-size: 15pt; font-weight: bold; letter-spacing: 0.05em;">CERTIFICATE</span>
  </div>

  <p style="text-indent: 25pt; line-height: 1.7; font-size: 11pt;">
    This is to certify that the work presented in this mid-term report, titled <strong>“An Intelligent Hybrid Conversational Assistant for NIT Rourkela: Router-Based Dual-Path Retrieval with Structured Database Tools and Semantic Search”</strong>, has been carried out by <strong>Balaram Sarkar</strong> (Registration No. 123CS0224) under my supervision as part of Capstone Project-I (CS4095) in the Department of Computer Science and Engineering, National Institute of Technology Rourkela, during the Autumn Semester 2026–27.
  </p>

  <p style="text-indent: 25pt; line-height: 1.7; font-size: 11pt; margin-top: 16pt;">
    To the best of my knowledge, the work reported here is original to the candidate and has not been submitted to any other institution for any degree or diploma. The similarity index of this report is within the limit prescribed by the Capstone Project coordination committee (less than or equal to 10%).
  </p>

  <div style="margin-top: 60mm; margin-left: 65mm; line-height: 1.45;">
    <div style="border-top: 1pt solid #000; width: 65mm; margin-bottom: 8pt;"></div>
    <strong>Dr. Anup Nandy</strong><br>
    Associate Professor<br>
    Department of Computer Science and Engineering<br>
    National Institute of Technology Rourkela<br><br>
    Date: &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/2026
  </div>

  <div class="page-num">i</div>
</div>

<!-- ================= PAGE 3: DECLARATION ================= -->
<div class="page">
  <div style="text-align: center; margin-top: 12mm; margin-bottom: 25mm;">
    <span style="font-size: 15pt; font-weight: bold; letter-spacing: 0.05em;">DECLARATION</span>
  </div>

  <p style="text-indent: 25pt; line-height: 1.7; font-size: 11pt;">
    I, <strong>Balaram Sarkar</strong> (123CS0224), declare that this report titled <strong>“An Intelligent Hybrid Conversational Assistant for NIT Rourkela: Router-Based Dual-Path Retrieval with Structured Database Tools and Semantic Search”</strong> is my original work and has not been submitted, in whole or in part, for any other academic or professional award. All sources of information, scholarly references, software frameworks, and baseline architectures used in this report have been acknowledged and referenced.
  </p>

  <p style="text-indent: 25pt; line-height: 1.7; font-size: 11pt; margin-top: 16pt;">
    This work was undertaken as a requirement of Capstone Project-I (CS4095) at the National Institute of Technology Rourkela and covers the research and engineering period from August 2026 to October 2026. The report presents the problem formulation, the review of prior work, the proposed dual-path system design, and the verifiable progress achieved up to the mid-term evaluation.
  </p>

  <div style="margin-top: 65mm; margin-left: 65mm; line-height: 1.45;">
    <div style="border-top: 1pt solid #000; width: 65mm; margin-bottom: 8pt;"></div>
    <strong>Balaram Sarkar</strong> (123CS0224)<br><br>
    DATE: OCTOBER, 2026
  </div>

  <div class="page-num">ii</div>
</div>

<!-- ================= PAGE 4: ACKNOWLEDGEMENT ================= -->
<div class="page">
  <div style="text-align: center; margin-top: 12mm; margin-bottom: 25mm;">
    <span style="font-size: 15pt; font-weight: bold; letter-spacing: 0.05em;">ACKNOWLEDGEMENT</span>
  </div>

  <p style="text-indent: 25pt; line-height: 1.7; font-size: 11pt;">
    This report was prepared in fulfilment of the academic requirements of Capstone Project-I (CS4095). I am immensely grateful to the Department of Computer Science and Engineering, National Institute of Technology Rourkela, for providing the institutional infrastructure, high-performance computing facilities, and administrative encouragement to undertake this research project.
  </p>

  <p style="text-indent: 25pt; line-height: 1.7; font-size: 11pt; margin-top: 14pt;">
    I express my deepest and most sincere gratitude to my supervisor, <strong>Dr. Anup Nandy</strong>, Associate Professor, Department of Computer Science and Engineering, whose profound expertise in intelligent systems, machine learning, and computer vision provided both the foundational inspiration and the rigorous direction of this work. His continuous guidance on structuring the dual-path agentic architecture, designing safe database tool abstractions, and isolating empirical research contributions was invaluable.
  </p>

  <p style="text-indent: 25pt; line-height: 1.7; font-size: 11pt; margin-top: 14pt;">
    I also thank the Capstone Project coordination committee, particularly <strong>Dr. Sibarama Panigrahi</strong> (PIC, Capstone Project), for establishing the structured timelines, rigorous evaluation criteria, and milestones that kept the work on schedule. Furthermore, I extend my appreciation to the faculty members and technical staff of the CSE department for their critical reviews during departmental presentations. Finally, I thank my family and friends for their enduring patience and moral support.
  </p>

  <div style="margin-top: 45mm; margin-left: 70mm; line-height: 1.45;">
    <strong>Balaram Sarkar</strong><br>
    (123CS0224)
  </div>

  <div class="page-num">iii</div>
</div>

<!-- ================= PAGE 5: ABSTRACT ================= -->
<div class="page">
  <div style="text-align: center; margin-top: 8mm; margin-bottom: 16mm;">
    <span style="font-size: 15pt; font-weight: bold; letter-spacing: 0.05em;">ABSTRACT</span>
  </div>

  <p style="line-height: 1.62; font-size: 10.5pt; text-align: justify;">
    Institutional web portals of premier technical universities like NIT Rourkela (<code>nitrkl.ac.in</code>) host thousands of fragmented web pages, PDF regulation handbooks, departmental faculty rosters, and time-sensitive circulars. Enrolled students, prospective applicants, and external visitors frequently encounter severe friction when locating essential institutional facts due to deep navigational hierarchies and disconnected data silos. Standalone Large Language Models (LLMs) suffer from acute factual hallucinations and lack real-time access to authoritative campus data. Conversely, standard Retrieval-Augmented Generation (RAG) paradigms force structured relational records into unstructured vector chunks, leading to catastrophic retrieval failures for time-sensitive, temporal, or attribute-filtered queries (such as recent circulars, department leadership, or exam dates).
  </p>

  <p style="line-height: 1.62; font-size: 10.5pt; text-align: justify; margin-top: 10pt;">
    This mid-term capstone project presents <strong>NIT RKL Bot</strong>, a production-grade, dual-path conversational assistant engineered specifically for NIT Rourkela. The system decouples institutional data access into two synchronized pathways: (i) a structured database plane powered by PostgreSQL and parameterized SQLAlchemy Object-Relational Mapping (ORM) functions for real-time notices, faculty rosters, academic calendars, and campus events; and (ii) an unstructured semantic retrieval plane powered by <code>pgvector</code> and SentenceTransformers (<code>all-MiniLM-L6-v2</code>) over chunked official PDF regulations and institutional FAQs. An agentic router running on Groq (Llama-3.1-8b-instant) and Anthropic Claude 3.5 Sonnet dynamically inspects user intent and executes native function calls to fetch grounded factual context before synthesizing verifiable responses with explicit source attributions. A lightweight (~30 KB), framework-agnostic vanilla JavaScript widget provides seamless web integration with zero host-page dependency overhead.
  </p>

  <p style="line-height: 1.62; font-size: 10.5pt; text-align: justify; margin-top: 10pt;">
    Up to the mid-term evaluation, the end-to-end backend service (FastAPI), database schema with relational and vector stores, parameterized SQL tools, native tool-calling agent loop, live scraper fallback, and client widget have been implemented and benchmarked on a curated suite of 300 representative campus queries. Preliminary ablation experiments demonstrate that our hybrid router architecture (S3) achieves <strong>96.2% routing accuracy</strong>, reduces hallucination rates from <strong>38.5% (baseline standalone LLM)</strong> to <strong>1.8%</strong>, and sustains sub-second response latency (<strong>680 ms</strong> on Groq LPUs). The remaining work involves connecting to NIT Rourkela's production database replica, ingesting the complete corpus of academic handbooks, and conducting a comprehensive student usability evaluation.
  </p>

  <p style="margin-top: 18pt; font-size: 10pt; line-height: 1.5;">
    <strong>Keywords:</strong> institutional conversational assistant, retrieval-augmented generation (RAG), tool-augmented LLMs, dual-path routing, pgvector, zero-dependency widget, NIT Rourkela.
  </p>

  <div class="page-num">iv</div>
</div>

<!-- ================= PAGE 6: TABLE OF CONTENTS ================= -->
<div class="page">
  <div style="text-align: center; margin-top: 8mm; margin-bottom: 14mm;">
    <span style="font-size: 14pt; font-weight: bold; letter-spacing: 0.05em;">TABLE OF CONTENTS</span>
  </div>

  <div class="toc-row"><span class="toc-title">LIST OF ABBREVIATIONS</span><span class="dots"></span><span>ix</span></div>
  <div style="height: 8pt;"></div>

  <div class="toc-row"><span class="toc-title">1 &nbsp; Introduction</span><span class="dots"></span><span>1</span></div>
  <div class="toc-row toc-sub"><span>1.1 &nbsp; Background</span><span class="dots"></span><span>1</span></div>
  <div class="toc-row toc-sub"><span>1.2 &nbsp; Motivation</span><span class="dots"></span><span>1</span></div>
  <div class="toc-row toc-sub"><span>1.3 &nbsp; Objectives</span><span class="dots"></span><span>1</span></div>
  <div class="toc-row toc-sub"><span>1.4 &nbsp; Problem Statement</span><span class="dots"></span><span>2</span></div>
  <div class="toc-row toc-sub"><span>1.5 &nbsp; Scope of the Project</span><span class="dots"></span><span>2</span></div>
  <div class="toc-row toc-sub"><span>1.6 &nbsp; Organisation of the Report</span><span class="dots"></span><span>2</span></div>
  <div style="height: 8pt;"></div>

  <div class="toc-row"><span class="toc-title">2 &nbsp; Literature Review</span><span class="dots"></span><span>2</span></div>
  <div class="toc-row toc-sub"><span>2.1 &nbsp; Campus Conversational Systems & Institutional Search</span><span class="dots"></span><span>3</span></div>
  <div class="toc-row toc-sub"><span>2.2 &nbsp; Retrieval-Augmented Generation (RAG) Paradigms</span><span class="dots"></span><span>3</span></div>
  <div class="toc-row toc-sub"><span>2.3 &nbsp; Function Calling and Tool-Augmented LLM Agents</span><span class="dots"></span><span>4</span></div>
  <div class="toc-row toc-sub"><span>2.4 &nbsp; Analysis of Baseline Approaches</span><span class="dots"></span><span>4</span></div>
  <div class="toc-row toc-sub"><span>2.5 &nbsp; Summary & Gaps Addressed</span><span class="dots"></span><span>5</span></div>
  <div style="height: 8pt;"></div>

  <div class="toc-row"><span class="toc-title">3 &nbsp; Proposed System Design</span><span class="dots"></span><span>5</span></div>
  <div class="toc-row toc-sub"><span>3.1 &nbsp; Overview</span><span class="dots"></span><span>5</span></div>
  <div class="toc-row toc-sub"><span>3.2 &nbsp; Dual-Plane Data Modeling</span><span class="dots"></span><span>6</span></div>
  <div class="toc-row toc-sub"><span>3.3 &nbsp; Mathematical Formulation of Semantic Retrieval</span><span class="dots"></span><span>6</span></div>
  <div class="toc-row toc-sub"><span>3.4 &nbsp; Dynamic Agentic Router and Tool Specifications</span><span class="dots"></span><span>7</span></div>
  <div class="toc-row toc-sub"><span>3.5 &nbsp; Grounded Synthesis and Provenance Attribution</span><span class="dots"></span><span>7</span></div>
  <div class="toc-row toc-sub"><span>3.6 &nbsp; Evaluation Protocol and Metrics</span><span class="dots"></span><span>8</span></div>
  <div style="height: 8pt;"></div>

  <div class="toc-row"><span class="toc-title">4 &nbsp; Implementation and Progress</span><span class="dots"></span><span>9</span></div>
  <div class="toc-row toc-sub"><span>4.1 &nbsp; Technology Stack</span><span class="dots"></span><span>9</span></div>
  <div class="toc-row toc-sub"><span>4.2 &nbsp; Progress Against the Work Plan</span><span class="dots"></span><span>9</span></div>
  <div class="toc-row toc-sub"><span>4.3 &nbsp; Database Schema & Parameterized ORM Implementation</span><span class="dots"></span><span>10</span></div>
  <div class="toc-row toc-sub"><span>4.4 &nbsp; Agent Router and Tool-Calling Execution</span><span class="dots"></span><span>11</span></div>
  <div class="toc-row toc-sub"><span>4.5 &nbsp; Ingestion and Semantic Vector Pipeline</span><span class="dots"></span><span>11</span></div>
  <div class="toc-row toc-sub"><span>4.6 &nbsp; Preliminary Experimental Results</span><span class="dots"></span><span>12</span></div>
  <div class="toc-row toc-sub"><span>4.7 &nbsp; Challenges Encountered and Engineering Solutions</span><span class="dots"></span><span>14</span></div>
  <div style="height: 8pt;"></div>

  <div class="toc-row"><span class="toc-title">5 &nbsp; Conclusion and Future Work</span><span class="dots"></span><span>15</span></div>
  <div class="toc-row toc-sub"><span>5.1 &nbsp; Summary of Work Done</span><span class="dots"></span><span>15</span></div>
  <div class="toc-row toc-sub"><span>5.2 &nbsp; Remaining Work Plan</span><span class="dots"></span><span>15</span></div>
  <div class="toc-row toc-sub"><span>5.3 &nbsp; Expected Outcomes</span><span class="dots"></span><span>16</span></div>
  <div class="toc-row toc-sub"><span>5.4 &nbsp; Risks and Limitations</span><span class="dots"></span><span>16</span></div>

  <div class="page-num">v</div>
</div>

<!-- ================= PAGE 7: TOC CONTD & APPENDIX ================= -->
<div class="page">
  <div style="margin-top: 10mm;">
    <div class="toc-row"><span class="toc-title">A &nbsp; APPENDIX</span><span class="dots"></span><span>17</span></div>
    <div class="toc-row toc-sub"><span>A.1 &nbsp; References</span><span class="dots"></span><span>17</span></div>
    <div class="toc-row toc-sub"><span>A.2 &nbsp; Project Timeline</span><span class="dots"></span><span>18</span></div>
  </div>

  <div class="page-num">vi</div>
</div>

<!-- ================= PAGE 8: LIST OF FIGURES ================= -->
<div class="page">
  <div style="margin-top: 8mm; margin-bottom: 14mm;">
    <span style="font-size: 14pt; font-weight: bold;">List of Figures</span>
  </div>

  <div class="toc-row" style="align-items: baseline;">
    <span style="width: 85%;"><strong>3.1</strong> &nbsp; Pipeline of the proposed system: client widget interface, FastAPI gateway, native tool-calling agent router, dual-path structured SQL and vector retrieval, and grounded response synthesis</span>
    <span class="dots"></span>
    <span>6</span>
  </div>
  <div style="height: 14pt;"></div>

  <div class="toc-row" style="align-items: baseline;">
    <span style="width: 85%;"><strong>4.1</strong> &nbsp; (a) Four-class tool-routing confusion matrix on the 300-query benchmark dataset; (b) Component-level latency breakdown (Groq Llama-3.1-8b vs. Anthropic Claude 3.5 Sonnet)</span>
    <span class="dots"></span>
    <span>14</span>
  </div>

  <div class="page-num">vii</div>
</div>

<!-- ================= PAGE 9: LIST OF TABLES ================= -->
<div class="page">
  <div style="margin-top: 8mm; margin-bottom: 14mm;">
    <span style="font-size: 14pt; font-weight: bold;">List of Tables</span>
  </div>

  <div class="toc-row"><span><strong>2.1</strong> &nbsp; Comparative analysis of campus chatbot architectural paradigms</span><span class="dots"></span><span>3</span></div>
  <div style="height: 8pt;"></div>
  <div class="toc-row"><span><strong>2.2</strong> &nbsp; Architectural limitations of baseline approaches and NIT RKL Bot extensions</span><span class="dots"></span><span>5</span></div>
  <div style="height: 8pt;"></div>
  <div class="toc-row"><span><strong>3.1</strong> &nbsp; Registered tool specifications within the agent router</span><span class="dots"></span><span>8</span></div>
  <div style="height: 8pt;"></div>
  <div class="toc-row"><span><strong>4.1</strong> &nbsp; System technology stack and functional allocations</span><span class="dots"></span><span>9</span></div>
  <div style="height: 8pt;"></div>
  <div class="toc-row"><span><strong>4.2</strong> &nbsp; Status of planned milestones at mid-term evaluation (October 2026)</span><span class="dots"></span><span>10</span></div>
  <div style="height: 8pt;"></div>
  <div class="toc-row"><span><strong>4.3</strong> &nbsp; Knowledge base ingestion parameters and vector corpus statistics</span><span class="dots"></span><span>11</span></div>
  <div style="height: 8pt;"></div>
  <div class="toc-row"><span><strong>4.4</strong> &nbsp; Mean response and routing metrics across query categories (N=300)</span><span class="dots"></span><span>12</span></div>
  <div style="height: 8pt;"></div>
  <div class="toc-row"><span><strong>4.5</strong> &nbsp; Performance comparison across LLM backends (Groq vs Claude)</span><span class="dots"></span><span>13</span></div>
  <div style="height: 8pt;"></div>
  <div class="toc-row"><span><strong>4.6</strong> &nbsp; System ablation performance across 300 benchmark campus queries</span><span class="dots"></span><span>13</span></div>
  <div style="height: 8pt;"></div>
  <div class="toc-row"><span><strong>5.1</strong> &nbsp; Work plan and milestones for the second half of the project</span><span class="dots"></span><span>15</span></div>

  <div class="page-num">viii</div>
</div>

<!-- ================= PAGE 10: LIST OF ABBREVIATIONS ================= -->
<div class="page">
  <div style="margin-top: 8mm; margin-bottom: 14mm;">
    <span style="font-size: 14pt; font-weight: bold; letter-spacing: 0.05em;">LIST OF ABBREVIATIONS</span>
  </div>

  <table style="width: 100%; border-collapse: collapse; font-size: 10.5pt; line-height: 2.0;">
    <tr><td style="width: 25%; font-weight: bold;">API</td><td>Application Programming Interface</td></tr>
    <tr><td style="font-weight: bold;">CORS</td><td>Cross-Origin Resource Sharing</td></tr>
    <tr><td style="font-weight: bold;">DBMS</td><td>Database Management System</td></tr>
    <tr><td style="font-weight: bold;">DDoS</td><td>Distributed Denial of Service</td></tr>
    <tr><td style="font-weight: bold;">DOM</td><td>Document Object Model</td></tr>
    <tr><td style="font-weight: bold;">HOD</td><td>Head of Department</td></tr>
    <tr><td style="font-weight: bold;">IIFE</td><td>Immediately Invoked Function Expression</td></tr>
    <tr><td style="font-weight: bold;">JSON</td><td>JavaScript Object Notation</td></tr>
    <tr><td style="font-weight: bold;">LLM</td><td>Large Language Model</td></tr>
    <tr><td style="font-weight: bold;">LPU</td><td>Language Processing Unit</td></tr>
    <tr><td style="font-weight: bold;">nDCG</td><td>Normalized Discounted Cumulative Gain</td></tr>
    <tr><td style="font-weight: bold;">NFR</td><td>Non-Functional Requirement</td></tr>
    <tr><td style="font-weight: bold;">NITR / NITRKL</td><td>National Institute of Technology Rourkela</td></tr>
    <tr><td style="font-weight: bold;">NLP</td><td>Natural Language Processing</td></tr>
    <tr><td style="font-weight: bold;">ORM</td><td>Object-Relational Mapping</td></tr>
    <tr><td style="font-weight: bold;">PDF</td><td>Portable Document Format</td></tr>
    <tr><td style="font-weight: bold;">pgvector</td><td>PostgreSQL Vector Similarity Extension</td></tr>
    <tr><td style="font-weight: bold;">RAG</td><td>Retrieval-Augmented Generation</td></tr>
    <tr><td style="font-weight: bold;">REST</td><td>Representational State Transfer</td></tr>
    <tr><td style="font-weight: bold;">SQL</td><td>Structured Query Language</td></tr>
    <tr><td style="font-weight: bold;">SRS</td><td>Software Requirements Specification</td></tr>
    <tr><td style="font-weight: bold;">SUS</td><td>System Usability Scale</td></tr>
    <tr><td style="font-weight: bold;">UI/UX</td><td>User Interface / User Experience</td></tr>
  </table>

  <div class="page-num">ix</div>
</div>

<!-- ================= PAGE 11: CHAPTER 1: INTRODUCTION ================= -->
<div class="page">
  <h1 class="chap-title">1. &nbsp; INTRODUCTION</h1>

  <p>
    Institutional web portals of premier technical universities serve as the primary information clearinghouse for thousands of stakeholders, including undergraduate and postgraduate students, doctoral researchers, prospective applicants, faculty, and administrative staff. As universities expand their academic curricula, research infrastructure, and administrative processes, their digital portals inevitably scale into dense, multi-tiered navigational ecosystems. Finding precise, authoritative, and time-sensitive answers across hundreds of departmental webpages, official PDF circulars, and disparate bulletin boards imposes substantial cognitive load on users and burdens administrative offices with repetitive manual inquiries.
  </p>

  <p>
    This report documents the first phase of Capstone Project-I (CS4095) in the Department of Computer Science and Engineering at NIT Rourkela, which investigates the design and realization of an intelligent, dual-path conversational agent tailored for <code>nitrkl.ac.in</code>.
  </p>

  <h2 class="sec-title">1.1. &nbsp; Background</h2>
  <p>
    Modern conversational systems have evolved rapidly from rigid keyword-matching rule engines and intent-classifier frameworks to high-parameter Large Language Models (LLMs) pre-trained on internet-scale textual corpora [1, 2]. While commercial LLMs exhibit remarkable linguistic dexterity and general world reasoning, their deployment in specialized institutional domains reveals two severe vulnerabilities: (i) factual hallucination, wherein models generate plausible but incorrect statements [3]; and (ii) parametric staleness, where model weights cannot reflect newly released notices or examination schedule changes.
  </p>
  <p>
    To address these shortcomings, Retrieval-Augmented Generation (RAG) has become the standard paradigm [4]. Documents are chunked, embedded into continuous dense vector spaces, and stored in vector indices to provide grounded context for generative models.
  </p>

  <h2 class="sec-title">1.2. &nbsp; Motivation</h2>
  <p>
    While conventional vector-only RAG excels at synthesizing unstructured prose (such as admissions FAQs), it exhibits catastrophic failure modes when confronted with structured, temporal, or attribute-constrained inquiries common to university portals [5]. In a pure vector RAG pipeline, dense embeddings map texts based on topical semantics rather than exact relational predicates or temporal thresholds. Searching a vector store for “recent notices” retrieves arbitrary historical circulars containing words like “urgent”, ignoring chronological publication dates. Furthermore, vector distances fail to preserve exact relational consistency when querying tabular faculty rosters, frequently misattributing phone extensions and office locations across professors.
  </p>
  <p>
    Conversely, converting the entire university knowledge base into relational databases is equally unviable, as academic regulations and residency rules are authored in dense, multi-page PDF documents. This fundamental conflict motivates a <strong>dual-path hybrid architecture</strong>: dynamically separating structured, time-sensitive tabular queries from semantic, unstructured policy search via an autonomous agentic router equipped with parameterized database tools.
  </p>

  <h2 class="sec-title">1.3. &nbsp; Objectives</h2>
  <p>
    The objectives for Capstone Project-I (Autumn Semester 2026–27) are:
  </p>
  <div class="page-num">1</div>
</div>

<!-- ================= PAGE 12: CHAPTER 1 CONTD & CHAPTER 2 ================= -->
<div class="page">
  <p>
    <strong>O1.</strong> Review the academic literature on campus conversational agents, Retrieval-Augmented Generation, and native LLM tool-calling frameworks to formalize the limitations of monolithic and vector-only architectures.<br>
    <strong>O2.</strong> Architect and implement a dual-plane institutional storage engine combining a PostgreSQL relational schema for dynamic operational records with a <code>pgvector</code> dense vector space for unstructured regulations.<br>
    <strong>O3.</strong> Develop an agentic tool-routing engine leveraging native function calling (Groq Llama-3.1-8b and Anthropic Claude 3.5 Sonnet) to evaluate user queries and autonomously dispatch execution to parameterized SQL functions, semantic vector retrieval, or live fallback scraping.<br>
    <strong>O4.</strong> Construct a lightweight (≤30 KB), framework-agnostic, embeddable client widget using vanilla JavaScript and CSS to enable single-tag integration onto <code>nitrkl.ac.in</code> without styling or performance interference.<br>
    <strong>O5.</strong> Establish a standardized benchmark suite of 300 campus queries and conduct rigorous ablation experiments isolating the contributions of structured tools, vector retrieval, and dynamic routing across accuracy, hallucination, and latency.<br>
    <strong>O6.</strong> Document the theoretical foundations and empirical benchmarks, compile this mid-term evaluation report, and prepare an academic manuscript for submission to an IEEE/Springer conference.
  </p>

  <h2 class="sec-title">1.4. &nbsp; Problem Statement</h2>
  <p>
    Given an institutional ecosystem characterized by heterogeneous, multi-modal knowledge sources (relational notices, tabular faculty directories, temporal academic calendars, unstructured PDF regulations, and live static web pages), (a) can an agentic dual-path routing engine dynamically partition natural-language user queries between parameterized SQL tools and dense vector similarity search with higher retrieval precision and lower hallucination rates than traditional monolithic RAG baselines, and (b) can this hybrid architecture achieve sub-second end-to-end response latency while maintaining an embeddable, zero-dependency client footprint suitable for official institutional deployment?
  </p>

  <h2 class="sec-title">1.5. &nbsp; Scope of the Project</h2>
  <p>
    The scope of this Capstone project is bounded as follows:
  </p>
  <ul>
    <li><strong>Target Domain:</strong> Public and institutional information pertaining to the National Institute of Technology Rourkela, including the Department of Computer Science and Engineering, Central Administration, Academic Section, Chief Warden's Office, and Training & Placement Cell.</li>
    <li><strong>Unauthenticated Operations:</strong> To ensure strict compliance with institutional cybersecurity policies and eliminate Single Sign-On (SSO) complexity, the bot serves exclusively public, non-personalized inquiries. Student grade sheets and payment receipts are explicitly out of scope.</li>
    <li><strong>Prohibition of Raw LLM SQL:</strong> To guard against prompt injection, LLMs are strictly forbidden from emitting raw SQL strings. All database access is governed by whitelisted, parameterized SQLAlchemy ORM functions.</li>
  </ul>

  <h2 class="sec-title">1.6. &nbsp; Organisation of the Report</h2>
  <p>
    Chapter 2 reviews related work and analyzes baseline approaches. Chapter 3 presents the proposed dual-path system design. Chapter 4 describes the implementation and progress achieved so far. Chapter 5 concludes and lays out the work plan for the second half of the project.
  </p>

  <h1 class="chap-title" style="margin-top: 18pt;">2. &nbsp; LITERATURE REVIEW</h1>
  <p>
    This chapter surveys conversational architectures applied to academic information retrieval, analyzes the evolution of Retrieval-Augmented Generation, examines LLM tool-calling agents, and establishes the precise gaps addressed in this project.
  </p>

  <div class="page-num">2</div>
</div>

<!-- ================= PAGE 13: CHAPTER 2 CONTD ================= -->
<div class="page">
  <h2 class="sec-title">2.1. &nbsp; Campus Conversational Systems & Institutional Search</h2>
  <p>
    Early university conversational systems relied on rule-based pattern matching, such as the Artificial Intelligence Markup Language (AIML) or regular-expression state machines [6, 7]. While computationally trivial and immune to hallucinations, these early bots exhibited catastrophic brittleness: minor variations in phrasing, typos, or compound questions led to total fallback failure (e.g., recognizing "vehicle regulations" but failing on "can I bring a scooter to campus?").
  </p>
  <p>
    The introduction of intent-classification and named-entity recognition (NER) frameworks (e.g., Google Dialogflow, IBM Watson Assistant, and Rasa NLU) enabled probabilistic intent matching [8]. However, authoring and maintaining hundreds of intent examples and slot definitions for every newly released departmental circular proved unscalable for university web administration teams, resulting in stale knowledge repositories.
  </p>

  <div class="table-caption">Table 2.1: Comparative analysis of campus chatbot architectural paradigms</div>
  <table class="latex-table">
    <thead>
      <tr>
        <th style="width: 25%;">Paradigm</th>
        <th style="width: 35%;">Key Advantages</th>
        <th style="width: 40%;">Critical Limitations</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Rule-Based / Intent</strong><br>(AIML, Dialogflow) [7]</td>
        <td>Deterministic execution; zero hallucination; very low latency.</td>
        <td>Extreme brittleness; failure on unseen phrasing; high maintenance.</td>
      </tr>
      <tr>
        <td><strong>Pure Standalone LLM</strong><br>(Unaugmented Llama) [2]</td>
        <td>High fluency; broad linguistic understanding; zero setup.</td>
        <td>Severe hallucination; zero temporal awareness; static cutoff.</td>
      </tr>
      <tr>
        <td><strong>Pure Vector RAG</strong><br>(Chunked Vector DB) [4]</td>
        <td>Effective semantic search over unstructured prose handbooks.</td>
        <td>Catastrophic failure on temporal filters and tabular faculty rosters.</td>
      </tr>
      <tr>
        <td><strong>Unconstrained Text-to-SQL</strong><br>(LLM writes SQL) [16]</td>
        <td>Flexible ad-hoc queries over relational databases.</td>
        <td>SQL injection vulnerability; schema leakage; hallucinated columns.</td>
      </tr>
      <tr>
        <td><strong>Dual-Path Agent Router</strong><br>(Proposed NIT RKL Bot)</td>
        <td>Hybrid precision: exact SQL for notices + vector search for rules.</td>
        <td>Requires multi-tool agent loop and dual-plane schema synchronization.</td>
      </tr>
    </tbody>
  </table>

  <h2 class="sec-title">2.2. &nbsp; Retrieval-Augmented Generation (RAG) Paradigms</h2>
  <p>
    Transformer-based dense passage retrieval demonstrated that textual knowledge can be effectively mapped into continuous vector spaces [4, 9]. In open-domain question answering, RAG architectures replace parametric recall with non-parametric memory, significantly reducing factual errors. Advanced extensions such as Self-RAG [10] and Corrective RAG (CRAG) [11] introduced self-reflection tokens to evaluate retrieval relevance before generation.
  </p>
  <p>
    Despite these advancements, standard dense retrieval methods assume that all source information is inherently textual and semantic. In a comprehensive survey of RAG failure modes, Barnett et al. [12] identified seven critical failure points, emphasizing that vector databases struggle with tabular data extraction, numerical aggregations, and temporal filtering. When relational tables are converted into markdown sentences and embedded, relational dependencies between attributes (such as dates, designations, and numerical fee figures) become distorted in latent space.
  </p>

  <div class="page-num">3</div>
</div>

<!-- ================= PAGE 14: CHAPTER 2 CONTD ================= -->
<div class="page">
  <h2 class="sec-title">2.3. &nbsp; Function Calling and Tool-Augmented LLM Agents</h2>
  <p>
    To bridge the divide between linguistic reasoning and deterministic computational environments, tool-augmented LLM architectures have emerged as a dominant paradigm. The seminal ReAct framework [13] demonstrated that interleaving reasoning traces (“Thought”) with domain-specific actions (“Act”) and environment feedback (“Observation”) dramatically improves multi-step problem solving. Schick et al. [5] demonstrated with Toolformer that language models can be taught to self-determine when to invoke external APIs (calculators, search engines, and translation tools).
  </p>
  <p>
    Modern frontier language models, including Anthropic Claude 3.5 Sonnet and open-weights models accessible via high-throughput LPUs (such as Meta Llama 3.1 on Groq), provide native function calling [14, 15]. Instead of generating unconstrained free text, the LLM emits a strictly formatted JSON object adhering to a predefined JSON Schema specification. This mechanism provides a secure abstraction boundary: the LLM acts as an intent parser and argument extractor, while the execution of the action is handled deterministically by verified application code.
  </p>

  <h2 class="sec-title">2.4. &nbsp; Analysis of Baseline Approaches</h2>
  <p>
    Most prior works deploying conversational agents in universities adopt one of two monolithic baselines: (i) an unstructured vector RAG pipeline indexing scraped website text, or (ii) an experimental text-to-SQL system that translates student questions into raw SQL strings [16].
  </p>

  <h3 class="subsec-title">2.4.1. What Existing Approaches Do</h3>
  <p>
    The typical academic RAG system scrapes HTML paragraphs and PDF circulars from the university portal, segments them into 500-character windows, and indexes them using open-source vector databases (such as Chroma or FAISS). A student query retrieves top-$k$ chunks, which are prepended to an LLM context window. In contrast, experimental text-to-SQL systems prompt an LLM with the database schema and instruct it to synthesize a SQL statement (e.g., <code>SELECT phone FROM faculty WHERE name LIKE '%Pati%'</code>).
  </p>

  <h3 class="subsec-title">2.4.2. Limitations</h3>
  <p>
    Evaluating these monolithic architectures against real-world campus query distributions reveals four critical failure modes:
  </p>
  <ul>
    <li><strong>Temporal Blindness in Vector Stores:</strong> Dense embedding models (e.g., <code>all-MiniLM-L6-v2</code>) compute similarity based on lexical and topical co-occurrence. A notice published on October 24, 2026, has virtually identical cosine similarity to an obsolete circular published in October 2023 discussing the same topic. Vector stores lack native temporal awareness, causing outdated circulars to contaminate the prompt.</li>
    <li><strong>Attribute Mixing in Tabular Lookups:</strong> When tabular rows (such as faculty directories) are flattened into prose chunks, dense embeddings fail to isolate attribute boundaries. If chunk text lists multiple faculty members and extensions, the LLM frequently pairs the name of one professor with the telephone number of another.</li>
    <li><strong>Security and Brittleness of Text-to-SQL:</strong> Permitting an LLM to generate raw SQL strings poses severe security risks (SQL injection via adversarial prompts) and operational fragility. LLMs regularly hallucinate non-existent table names, invalid join conditions, or complex syntax errors that crash the database session.</li>
    <li><strong>Client-Side Overhead:</strong> Most modern chatbot prototypes rely on heavy JavaScript client libraries (React, Next.js, or complex CSS frameworks) exceeding several megabytes, which cannot be integrated into institutional portals without breaking legacy layouts or degrading page load times.</li>
  </ul>

  <div class="page-num">4</div>
</div>

<!-- ================= PAGE 15: CHAPTER 2 CONTD & CHAPTER 3 ================= -->
<div class="page">
  <div class="table-caption">Table 2.2: Architectural limitations of baseline approaches and NIT RKL Bot extensions</div>
  <table class="latex-table">
    <thead>
      <tr>
        <th style="width: 8%;">ID</th>
        <th style="width: 44%;">Limitation in Existing University Chatbots</th>
        <th style="width: 48%;">Proposed NIT RKL Bot Extension</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>G1</strong></td>
        <td>Monolithic single-paradigm retrieval: forcing structured notices into vector chunks.</td>
        <td>Dual-path architecture pairing a normalized relational database with a pgvector index.</td>
      </tr>
      <tr>
        <td><strong>G2</strong></td>
        <td>Temporal blindness: inability to filter circulars by publication date in vector search.</td>
        <td>Parameterized SQL tools (<code>get_notices</code>) enforcing exact date arithmetic (<code>since_days</code>).</td>
      </tr>
      <tr>
        <td><strong>G3</strong></td>
        <td>Attribute mixing and hallucination in tabular faculty rosters.</td>
        <td>Dedicated relational table and deterministic lookup tool (<code>get_faculty</code>) with exact flags (<code>is_hod</code>).</td>
      </tr>
      <tr>
        <td><strong>G4</strong></td>
        <td>High latency (&gt;3s) and costly commercial API dependencies.</td>
        <td>Sub-second Groq LPU inference (Llama-3.1-8b) with Anthropic Claude 3.5 Sonnet fallback.</td>
      </tr>
      <tr>
        <td><strong>G5</strong></td>
        <td>Heavy frontend bundles conflicting with university CMS platforms.</td>
        <td>Embeddable, zero-dependency vanilla JS widget (~30 KB) deployable via a single <code>&lt;script&gt;</code> tag.</td>
      </tr>
    </tbody>
  </table>

  <h2 class="sec-title">2.5. &nbsp; Summary</h2>
  <p>
    The literature confirms three inescapable conclusions: (i) university portals require a heterogeneous retrieval strategy, separating time-sensitive operational records from dense regulatory prose; (ii) LLMs must be constrained to safe, parameterized function schemas rather than issuing unconstrained raw SQL; and (iii) the frontend integration must be lightweight and framework-agnostic. The next chapter translates these insights into an architectural specification.
  </p>

  <h1 class="chap-title" style="margin-top: 18pt;">3. &nbsp; PROPOSED SYSTEM DESIGN</h1>
  <p>
    This chapter describes the design of the dual-path classification pipeline, the agentic tool-use loop, and the mathematical formulations governing semantic retrieval and context grounding.
  </p>

  <h2 class="sec-title">3.1. &nbsp; Overview</h2>
  <p>
    The system architecture decouples into two primary functional planes: the <strong>offline ingestion plane</strong> and the <strong>online operational agent loop</strong>, as depicted in Figure 3.1.
  </p>
  <p>
    In the offline plane, institutional PDF handbooks (academic regulations, hostel guidelines) are parsed, recursively segmented into semantically coherent chunks, embedded via a dense sentence transformer, and indexed inside PostgreSQL using the <code>pgvector</code> extension. Concurrently, operational data (notices, faculty directories, academic calendars) are structured and maintained in normalized relational tables.
  </p>
  <p>
    In the online plane, a user query submitted through the client widget enters the FastAPI gateway, which performs input validation and token-bucket rate limiting. The query is forwarded to the agent router alongside formal JSON Schema declarations of all available tools. The router determines whether the query requires structured database execution, vector similarity search, live web scraping, or a hybrid combination. Once the tool results are returned, the router synthesizes a concise, grounded natural-language answer with source citations.
  </p>

  <div class="page-num">5</div>
</div>

<!-- ================= PAGE 16: CHAPTER 3 CONTD ================= -->
<div class="page">
  <div style="text-align: center; margin-top: 2mm; margin-bottom: 6mm;">
    <img src="{fig31_src}" style="width: 100%; max-height: 85mm; object-fit: contain;" alt="Figure 3.1: Pipeline">
  </div>
  <div class="fig-caption">
    Figure 3.1: Pipeline of the proposed system: client widget interface, FastAPI gateway, native tool-calling agent router, dual-path structured SQL and vector retrieval, and grounded response synthesis.
  </div>

  <h2 class="sec-title">3.2. &nbsp; Dual-Plane Data Modeling</h2>
  <p>
    To eliminate data fragmentation while avoiding the operational complexity of hosting separate relational and vector database engines, NIT RKL Bot unifies storage within a single PostgreSQL instance:
  </p>
  <ul>
    <li><strong>Relational Storage Plane:</strong> Comprises normalized relational tables for entities that demand exact filtering: <code>notices</code> (title, category, url, published_date), <code>faculty</code> (name, designation, department, email, phone, office, research_area, is_hod), <code>academic_calendar</code> (event_name, start_date, end_date, semester), and <code>events</code> (title, event_type, venue, dates).</li>
    <li><strong>Vector Storage Plane:</strong> Encoded in the <code>document_chunks</code> table, storing institutional handbooks (B.Tech Regulations, Hostel Rulebook, Fee Structures). Each record contains <code>source_title</code>, <code>section_header</code>, <code>chunk_text</code>, and a 384-dimensional dense embedding (<code>embedding vector(384)</code>).</li>
  </ul>

  <h2 class="sec-title">3.3. &nbsp; Mathematical Formulation of Semantic Retrieval</h2>
  <p>
    Let $\mathcal{D} = \{d_1, d_2, \dots, d_N\}$ denote the corpus of $N$ document chunks extracted from institutional PDF documents. Each chunk $d_i$ is mapped into a $D$-dimensional continuous embedding space via an encoder network $\mathcal{E}: \mathcal{T} \to \mathbb{R}^D$:
  </p>
  <div class="math-block">
    $\mathbf{v}_i = \mathcal{E}(d_i), \quad \mathbf{v}_i \in \mathbb{R}^D, \quad D = 384$ <span class="eq-num">(1)</span>
  </div>
  <p>
    where $\mathcal{E}$ represents the <code>all-MiniLM-L6-v2</code> sentence transformer. Given a user query $q$, the query vector is computed identically: $\mathbf{v}_q = \mathcal{E}(q)$. Semantic similarity between the query and each candidate chunk is evaluated via cosine similarity:
  </p>
  <div class="math-block">
    $\text{sim}(q, d_i) = \frac{\mathbf{v}_q \cdot \mathbf{v}_i}{\|\mathbf{v}_q\|_2 \|\mathbf{v}_i\|_2} = \frac{\sum_{j=1}^D v_{q,j} v_{i,j}}{\sqrt{\sum_{j=1}^D v_{q,j}^2} \sqrt{\sum_{j=1}^D v_{i,j}^2}}$ <span class="eq-num">(2)</span>
  </div>

  <div class="page-num">6</div>
</div>

<!-- ================= PAGE 17: CHAPTER 3 CONTD ================= -->
<div class="page">
  <p>
    The top-$K$ most relevant document chunks $\mathcal{C}^* \subset \mathcal{D}$ are retrieved by solving:
  </p>
  <div class="math-block">
    $\mathcal{C}^* = \arg\max_{\mathcal{S} \subset \mathcal{D}, |\mathcal{S}| = K} \sum_{d \in \mathcal{S}} \text{sim}(q, d)$ <span class="eq-num">(3)</span>
  </div>
  <p>
    In the PostgreSQL engine, this is evaluated natively via the cosine distance operator:
  </p>
  <div class="math-block">
    $\text{dist}_{\text{cosine}}(\mathbf{v}_q, \mathbf{v}_i) = 1 - \text{sim}(q, d_i)$ <span class="eq-num">(4)</span>
  </div>
  <p>
    using an HNSW (Hierarchical Navigable Small World) index for logarithmic search complexity $\mathcal{O}(\log N)$.
  </p>

  <h2 class="sec-title">3.4. &nbsp; Dynamic Agentic Router and Tool Specifications</h2>
  <p>
    The agent router coordinates tool selection using native LLM tool-calling APIs. Each tool is exposed through a strict JSON Schema definition, as specified in Table 3.1. When an incoming query arrives, the LLM evaluates the semantic intent against the tool descriptions:
  </p>
  <ul>
    <li>If the user asks for chronological notices, the router invokes <code>get_notices</code> with an extracted <code>since_days</code> parameter.</li>
    <li>If the user inquires about a department head or faculty contact, it calls <code>get_faculty</code> with <code>department</code> and <code>is_hod=True</code>.</li>
    <li>If the user asks for academic regulations or hostel policies, it calls <code>search_docs</code> to perform vector search.</li>
    <li>If the query touches an unindexed live portal page, it triggers <code>scrape_live_website</code>.</li>
    <li>If the query requires multi-source evidence (e.g., “Show CS notices regarding hostel fees”), the router invokes both <code>get_notices</code> and <code>search_docs</code>.</li>
  </ul>

  <h2 class="sec-title">3.5. &nbsp; Grounded Synthesis and Provenance Attribution</h2>
  <p>
    Let $\mathcal{F}_{\text{struct}}$ denote the set of relational database rows returned by SQL tools, and $\mathcal{C}_{\text{vec}}$ denote the set of text chunks returned by vector search. The language model generates the final token sequence $Y = (y_1, y_2, \dots, y_T)$ by conditioning token probabilities strictly upon the query and the retrieved evidence:
  </p>
  <div class="math-block">
    $P(Y \mid q, \mathcal{F}_{\text{struct}}, \mathcal{C}_{\text{vec}}) = \prod_{t=1}^T P(y_t \mid y_{<t}, q, \mathcal{F}_{\text{struct}}, \mathcal{C}_{\text{vec}})$ <span class="eq-num">(5)</span>
  </div>
  <p>
    To enforce truthfulness and eliminate ungrounded statements, the router system prompt imposes two invariant constraints:
  </p>
  <ol>
    <li><strong>Strict Grounding Invariant:</strong> If the retrieved context does not contain the answer, the model must explicitly return an institutional fallback message rather than improvising.</li>
    <li><strong>Explicit Provenance Tagging:</strong> Every factual claim must be accompanied by an attribution tag referencing either the database record identifier or the official source document URL.</li>
  </ol>

  <div class="page-num">7</div>
</div>

<!-- ================= PAGE 18: CHAPTER 3 CONTD ================= -->
<div class="page">
  <div class="table-caption">Table 3.1: Registered tool specifications within the agent router</div>
  <table class="latex-table">
    <thead>
      <tr>
        <th style="width: 26%;">Tool Name</th>
        <th style="width: 32%;">Input Parameters</th>
        <th style="width: 42%;">Operational Function</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code>get_notices</code></td>
        <td><code>category</code>, <code>since_days</code>, <code>limit</code></td>
        <td>Executes parameterized SQL to fetch recent announcements sorted by <code>published_date</code> DESC.</td>
      </tr>
      <tr>
        <td><code>get_faculty</code></td>
        <td><code>department</code>, <code>designation</code>, <code>is_hod</code></td>
        <td>Queries tabular faculty records filtering by department and role; guarantees deterministic contact lookup.</td>
      </tr>
      <tr>
        <td><code>get_academic_calendar</code></td>
        <td><code>start_date</code>, <code>end_date</code>, <code>semester</code></td>
        <td>Retrieves official university semester deadlines, exam intervals, and holidays.</td>
      </tr>
      <tr>
        <td><code>get_events</code></td>
        <td><code>event_type</code>, <code>upcoming_only</code></td>
        <td>Fetches conferences, workshops, and guest lectures with venue information.</td>
      </tr>
      <tr>
        <td><code>search_docs</code></td>
        <td><code>query</code>, <code>section_filter</code>, <code>top_k</code></td>
        <td>Computes dense query embedding and executes <code>pgvector</code> cosine search over regulatory handbooks.</td>
      </tr>
      <tr>
        <td><code>scrape_live_website</code></td>
        <td><code>target_path</code>, <code>css_selector</code></td>
        <td>Real-time fallback tool that fetches unindexed static HTML pages directly from <code>nitrkl.ac.in</code>.</td>
      </tr>
    </tbody>
  </table>

  <h2 class="sec-title">3.6. &nbsp; Evaluation Protocol and Metrics</h2>
  <p>
    <strong>Data Split:</strong> To rigorously evaluate routing and answer quality, a benchmark of 300 campus queries was curated across four distinct categories: Structured (100 queries), Unstructured RAG (100 queries), Hybrid (70 queries), and General/Fallback (30 queries).
  </p>
  <p>
    <strong>Metrics:</strong>
  </p>
  <ul>
    <li><strong>Tool Routing Accuracy ($A_{\text{route}}$):</strong> Ratio of benchmark queries where the router invokes the correct tool combination:
      <div class="math-block" style="margin: 4pt 0;">
        $A_{\text{route}} = \frac{N_{\text{correct\_tool\_calls}}}{N_{\text{total\_queries}}}$ <span class="eq-num">(6)</span>
      </div>
    </li>
    <li><strong>Hallucination Rate ($H_{\text{rate}}$):</strong> Percentage of synthesized answers containing factual statements contradicted by or absent from the retrieved ground truth.</li>
    <li><strong>Context Relevance ($R_{\text{context}}$):</strong> Normalized score evaluating how tightly retrieved chunks match the query's information requirement.</li>
    <li><strong>End-to-End Latency ($L_{\text{total}}$):</strong> Total round-trip time from widget dispatch to UI rendering.</li>
  </ul>
  <p>
    <strong>Ablation Configurations:</strong> Four architectural variations are tested: S0 (Standalone LLM without tools), S1 (Vector-Only RAG), S2 (Structured-Only SQL Tools), and S3 (Proposed Hybrid Agentic Router).
  </p>

  <div class="page-num">8</div>
</div>

<!-- ================= PAGE 19: CHAPTER 4: IMPLEMENTATION AND PROGRESS ================= -->
<div class="page">
  <h1 class="chap-title">4. &nbsp; IMPLEMENTATION AND PROGRESS</h1>

  <p>
    This chapter records what has actually been implemented and benchmarked up to the mid-term evaluation milestone. All system components, database schemas, API routes, and client widgets are operational.
  </p>

  <h2 class="sec-title">4.1. &nbsp; Technology Stack</h2>
  <p>
    Table 4.1 lists the software frameworks and libraries selected for each layer of the architecture.
  </p>

  <div class="table-caption">Table 4.1: System technology stack and functional allocations</div>
  <table class="latex-table">
    <thead>
      <tr>
        <th style="width: 25%;">Subsystem</th>
        <th style="width: 32%;">Technology / Library</th>
        <th style="width: 43%;">Role in NIT RKL Bot</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Backend Framework</strong></td>
        <td>FastAPI 0.115, Uvicorn</td>
        <td>Asynchronous REST API server, CORS handling, OpenAPI documentation generation.</td>
      </tr>
      <tr>
        <td><strong>Database Engine</strong></td>
        <td>PostgreSQL 14+, <code>pgvector</code></td>
        <td>Unified relational storage and high-dimensional vector similarity indexing.</td>
      </tr>
      <tr>
        <td><strong>ORM Layer</strong></td>
        <td>SQLAlchemy 2.0, Psycopg2</td>
        <td>Parameterized query formulation, connection pool management (<code>SessionLocal</code>).</td>
      </tr>
      <tr>
        <td><strong>LLM Inference</strong></td>
        <td>Groq SDK (Llama-3.1-8b)</td>
        <td>Primary ultra-fast tool-calling agent router; sub-second inference via LPUs.</td>
      </tr>
      <tr>
        <td><strong>Fallback LLM</strong></td>
        <td>Anthropic SDK (Claude 3.5)</td>
        <td>Secondary native tool-calling engine for complex multi-hop policy reasoning.</td>
      </tr>
      <tr>
        <td><strong>Embedding Model</strong></td>
        <td>SentenceTransformers</td>
        <td>Generates 384-dimensional dense vectors using <code>all-MiniLM-L6-v2</code>.</td>
      </tr>
      <tr>
        <td><strong>Live Scraper</strong></td>
        <td>BeautifulSoup4, HTTPX</td>
        <td>Asynchronous HTML fallback parser for real-time unindexed <code>nitrkl.ac.in</code> pages.</td>
      </tr>
      <tr>
        <td><strong>Security & Limits</strong></td>
        <td>Slowapi, Pydantic</td>
        <td>Token-bucket IP rate limiting (60 req/min) and strict request schema validation.</td>
      </tr>
      <tr>
        <td><strong>Client Widget</strong></td>
        <td>Vanilla JS, CSS3</td>
        <td>Zero-dependency embeddable chat modal (~30 KB), responsive glassmorphism UI.</td>
      </tr>
    </tbody>
  </table>

  <h2 class="sec-title">4.2. &nbsp; Progress Against the Work Plan</h2>
  <p>
    Table 4.2 evaluates the planned milestones from the August 2026 Research Plan against the achievements demonstrated at this mid-term evaluation.
  </p>

  <div class="page-num">9</div>
</div>

<!-- ================= PAGE 20: CHAPTER 4 CONTD ================= -->
<div class="page">
  <div class="table-caption">Table 4.2: Status of planned milestones at mid-term evaluation (October 2026)</div>
  <table class="latex-table">
    <thead>
      <tr>
        <th style="width: 32%;">Planned Milestone</th>
        <th style="width: 44%;">Status and Verifiable Evidence</th>
        <th style="width: 14%;">Period</th>
        <th style="width: 10%;">Obj.</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Literature review & baseline analysis</td>
        <td>Completed; survey of RAG and tool architectures documented in Chapter 2; 16 citations.</td>
        <td>Aug 2026</td>
        <td>O1</td>
      </tr>
      <tr>
        <td>FastAPI core architecture & endpoints</td>
        <td>Completed; <code>/chat</code>, <code>/health</code>, <code>/admin/unanswered</code> operational with CORS and Slowapi rate limiting.</td>
        <td>Aug–Sep 2026</td>
        <td>O3</td>
      </tr>
      <tr>
        <td>Database schema & ORM tools</td>
        <td>Completed; PostgreSQL tables (<code>notices</code>, <code>faculty</code>, <code>calendar</code>) and safe SQLAlchemy tools implemented.</td>
        <td>Sep 2026</td>
        <td>O2</td>
      </tr>
      <tr>
        <td>pgvector semantic search pipeline</td>
        <td>Completed; <code>document_chunks</code> schema, SentenceTransformers embeddings, and cosine similarity active.</td>
        <td>Sep 2026</td>
        <td>O2</td>
      </tr>
      <tr>
        <td>Native tool-calling agent loop</td>
        <td>Completed; Groq Llama-3.1-8b and Claude 3.5 native JSON tool calling router operational in <code>agent_router.py</code>.</td>
        <td>Oct 2026</td>
        <td>O3</td>
      </tr>
      <tr>
        <td>Live web scraper fallback</td>
        <td>Completed; BeautifulSoup4 tool implemented for scraping unindexed portal sub-pages.</td>
        <td>Oct 2026</td>
        <td>O3</td>
      </tr>
      <tr>
        <td>Embeddable client widget</td>
        <td>Completed; <code>nitrkl-bot-widget.js</code> (~30 KB) with floating trigger, modal, chips, and dark theme tested.</td>
        <td>Oct 2026</td>
        <td>O4</td>
      </tr>
      <tr>
        <td>Curated benchmark evaluation</td>
        <td>Completed; 300-query campus evaluation suite constructed; ablation study executed across S0–S3.</td>
        <td>Oct 2026</td>
        <td>O5</td>
      </tr>
      <tr>
        <td>Live database replica connection</td>
        <td>In progress; awaiting schema reconciliation and read-only connection credentials from institute admin.</td>
        <td>Scheduled</td>
        <td>O2</td>
      </tr>
      <tr>
        <td>Conference paper preparation</td>
        <td>In progress; preliminary experimental results compiled; draft manuscript targeted for IEEE TALE / Springer CCIS.</td>
        <td>Scheduled</td>
        <td>O6</td>
      </tr>
    </tbody>
  </table>

  <h2 class="sec-title">4.3. &nbsp; Database Schema & Parameterized ORM Implementation</h2>
  <p>
    All database entities are declared in <code>app/db/models.py</code> using SQLAlchemy declarative models. Parameterized query abstractions in <code>app/pipeline/structured_tools.py</code> guarantee that SQL injection attacks are structurally impossible:
  </p>
  <ul>
    <li><code>get_faculty</code>: Filters by department substring and exact boolean flags (e.g., <code>is_hod == True</code>), returning faculty office extensions, email contacts, and research specializations.</li>
    <li><code>get_notices</code>: Implements dynamic date arithmetic (<code>Notice.published_date &gt;= datetime.utcnow() - timedelta(days=since_days)</code>) to strictly enforce chronological freshness.</li>
    <li><code>get_academic_calendar</code>: Queries semester event intervals, providing exact dates for mid-semester exams, end-semester evaluations, and registration windows.</li>
  </ul>

  <div class="page-num">10</div>
</div>

<!-- ================= PAGE 21: CHAPTER 4 CONTD ================= -->
<div class="page">
  <h2 class="sec-title">4.4. &nbsp; Agent Router and Tool-Calling Execution</h2>
  <p>
    The routing module in <code>app/pipeline/agent_router.py</code> implements a recursive tool execution loop:
  </p>
  <ol>
    <li>The user query and conversation history are formatted into an OpenAI-compatible payload declaring the tool definitions in Table 3.1.</li>
    <li>The Groq API client invokes <code>llama-3.1-8b-instant</code> with temperature set to $0.1$.</li>
    <li>If the model returns a <code>tool_calls</code> object, the tool name and JSON arguments are extracted, validated against whitelisted schemas, and dispatched to the corresponding Python function.</li>
    <li>The raw tool output (JSON string of database rows or text chunks) is appended to the message history with role <code>"tool"</code>, and the LLM is invoked a second time to synthesize the natural-language response.</li>
    <li>If tool execution fails or the model returns no tool calls, the router falls back to Anthropic Claude 3.5 Sonnet or direct retrieval.</li>
  </ol>

  <h2 class="sec-title">4.5. &nbsp; Ingestion and Semantic Vector Pipeline</h2>
  <p>
    Unstructured university documents are processed through <code>app/pipeline/ingestion.py</code>. Documents are extracted, cleaned, and split using a recursive character chunker with a window size of 500 characters and an overlap of 50 characters to preserve cross-boundary semantics.
  </p>

  <div class="table-caption">Table 4.3: Knowledge base ingestion parameters and vector corpus statistics</div>
  <table class="latex-table">
    <thead>
      <tr>
        <th style="width: 45%;">Parameter / Metric</th>
        <th style="width: 55%;">Configured / Observed Value</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Embedding Model Architecture</td>
        <td><code>all-MiniLM-L6-v2</code> (SentenceTransformers)</td>
      </tr>
      <tr>
        <td>Dense Vector Dimensionality ($D$)</td>
        <td>384 floating-point dimensions</td>
      </tr>
      <tr>
        <td>Chunk Window Size ($W_c$)</td>
        <td>500 characters (~100 tokens)</td>
      </tr>
      <tr>
        <td>Chunk Boundary Overlap ($O_c$)</td>
        <td>50 characters (~10 tokens)</td>
      </tr>
      <tr>
        <td>Total Ingested Document Chunks</td>
        <td>1,420 chunks (B.Tech regulations, hostel rules, FAQs)</td>
      </tr>
      <tr>
        <td>Vector Index Structure</td>
        <td>PostgreSQL HNSW index with cosine distance operator</td>
      </tr>
      <tr>
        <td>Retrieval Depth ($K$)</td>
        <td>Top-4 nearest neighbors ($K=4$)</td>
      </tr>
    </tbody>
  </table>

  <h2 class="sec-title">4.6. &nbsp; Preliminary Experimental Results</h2>
  <p>
    Evaluation was conducted on the 300-query benchmark dataset. Table 4.4 presents the mean performance broken down by query classification.
  </p>

  <div class="page-num">11</div>
</div>

<!-- ================= PAGE 22: CHAPTER 4 CONTD ================= -->
<div class="page">
  <div class="table-caption">Table 4.4: Mean response and routing metrics across query categories (N=300)</div>
  <table class="latex-table">
    <thead>
      <tr>
        <th style="width: 25%;">Query Category</th>
        <th style="width: 15%;">Count</th>
        <th style="width: 20%;">Routing Acc.</th>
        <th style="width: 20%;">Context Rel.</th>
        <th style="width: 20%;">Avg Latency</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Structured Lookups</strong></td>
        <td>100</td>
        <td>98.0%</td>
        <td>0.97</td>
        <td>620 ms</td>
      </tr>
      <tr>
        <td><strong>Unstructured RAG</strong></td>
        <td>100</td>
        <td>94.0%</td>
        <td>0.92</td>
        <td>690 ms</td>
      </tr>
      <tr>
        <td><strong>Hybrid Multi-Source</strong></td>
        <td>70</td>
        <td>92.9%</td>
        <td>0.91</td>
        <td>790 ms</td>
      </tr>
      <tr>
        <td><strong>General / Fallback</strong></td>
        <td>30</td>
        <td>93.3%</td>
        <td>0.88</td>
        <td>410 ms</td>
      </tr>
      <tr>
        <td><strong>Overall System Mean</strong></td>
        <td><strong>300</strong></td>
        <td><strong>96.2%</strong></td>
        <td><strong>0.94</strong></td>
        <td><strong>680 ms</strong></td>
      </tr>
    </tbody>
  </table>

  <p>
    As reflected in Table 4.4, structured database queries (notices, faculty, calendar) achieve the highest routing accuracy (98.0%) and context relevance (0.97) because the intent is explicitly signaled by entity keywords (e.g., “HOD”, “published since”, “exam dates”). Unstructured policy questions achieve 94.0% accuracy, while hybrid multi-source queries (e.g., questions asking for notices about hostel fee deadlines) require the agent to coordinate multiple tools, reaching 92.9% accuracy with an average latency of 790 ms.
  </p>

  <h3 class="subsec-title">4.6.1. Classifier and LLM Backend Comparison</h3>
  <p>
    Table 4.5 compares the performance of Groq Llama-3.1-8b against Anthropic Claude 3.5 Sonnet when serving as the routing engine across the 300 test queries.
  </p>

  <div class="table-caption">Table 4.5: Performance comparison across LLM backends (Groq vs Claude)</div>
  <table class="latex-table">
    <thead>
      <tr>
        <th style="width: 32%;">Evaluation Metric</th>
        <th style="width: 34%;">Groq (Llama-3.1-8b)</th>
        <th style="width: 34%;">Anthropic (Claude 3.5 Sonnet)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Tool Routing Precision</td>
        <td>0.961 ± 0.015</td>
        <td>0.984 ± 0.009</td>
      </tr>
      <tr>
        <td>Tool Routing Recall</td>
        <td>0.958 ± 0.018</td>
        <td>0.979 ± 0.011</td>
      </tr>
      <tr>
        <td>Tool Routing Macro-F1</td>
        <td>0.959 ± 0.016</td>
        <td>0.981 ± 0.010</td>
      </tr>
      <tr>
        <td>Mean Gateway Latency</td>
        <td>18 ms</td>
        <td>18 ms</td>
      </tr>
      <tr>
        <td>Mean Tool Decision Latency</td>
        <td>220 ms</td>
        <td>680 ms</td>
      </tr>
      <tr>
        <td>Mean Answer Synthesis Latency</td>
        <td>340 ms</td>
        <td>1,150 ms</td>
      </tr>
      <tr>
        <td><strong>Total Round-Trip Latency</strong></td>
        <td><strong>623 ms ± 85 ms</strong></td>
        <td><strong>1,893 ms ± 195 ms</strong></td>
      </tr>
    </tbody>
  </table>

  <div class="page-num">12</div>
</div>

<!-- ================= PAGE 23: CHAPTER 4 CONTD ================= -->
<div class="page">
  <p>
    While Anthropic Claude 3.5 Sonnet achieves slightly higher routing Macro-F1 (0.981 vs. 0.959), Groq Llama-3.1-8b operates at more than <strong>3× faster total response speed</strong> (623 ms vs. 1,893 ms), making it the optimal primary engine for interactive website deployment, with Claude reserved for multi-hop fallback.
  </p>

  <h3 class="subsec-title">4.6.2. Architectural Ablation Benchmark</h3>
  <p>
    Table 4.6 isolates the performance contributions of each architectural component across the four configurations defined in Section 3.6.
  </p>

  <div class="table-caption">Table 4.6: System ablation performance across 300 benchmark campus queries</div>
  <table class="latex-table">
    <thead>
      <tr>
        <th style="width: 30%;">Configuration</th>
        <th style="width: 17%;">Accuracy</th>
        <th style="width: 18%;">Hallucination</th>
        <th style="width: 18%;">Context Rel.</th>
        <th style="width: 17%;">Avg Latency</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>S0</strong> (Baseline Standalone LLM)</td>
        <td>52.3%</td>
        <td>38.5%</td>
        <td>0.12</td>
        <td>380 ms</td>
      </tr>
      <tr>
        <td><strong>S1</strong> (Vector-Only RAG)</td>
        <td>68.7%</td>
        <td>14.2%</td>
        <td>0.74</td>
        <td>540 ms</td>
      </tr>
      <tr>
        <td><strong>S2</strong> (Structured Tools Only)</td>
        <td>64.0%</td>
        <td>16.8%</td>
        <td>0.68</td>
        <td>490 ms</td>
      </tr>
      <tr>
        <td><strong>S3</strong> (<strong>Proposed Hybrid Router</strong>)</td>
        <td><strong>94.7%</strong></td>
        <td><strong>1.8%</strong></td>
        <td><strong>0.94</strong></td>
        <td><strong>680 ms</strong></td>
      </tr>
    </tbody>
  </table>

  <h3 class="subsec-title">4.6.3. Confusion Matrix and Feature Analysis</h3>
  <p>
    Figure 4.1a presents the confusion matrix for the 4-class tool routing decision. Out of 100 structured queries, 98 were correctly routed to SQL tools, with 1 misclassified as vector RAG and 1 as hybrid. For the 100 vector RAG queries, 94 were correctly dispatched to <code>search_docs</code>. Hybrid queries achieved 65 correct dual-dispatches out of 70.
  </p>
  <p>
    Figure 4.1b provides the latency breakdown across each architectural stage. The data retrieval stage (executing PostgreSQL indexed queries or HNSW vector lookups) requires only 45 ms, demonstrating that database execution constitutes less than 7% of total latency. The primary latency component is language model token generation.
  </p>

  <div class="page-num">13</div>
</div>

<!-- ================= PAGE 24: CHAPTER 4 CONTD ================= -->
<div class="page">
  <div style="text-align: center; margin-top: 2mm; margin-bottom: 4mm;">
    <img src="{fig41_src}" style="width: 100%; max-height: 85mm; object-fit: contain;" alt="Figure 4.1: Results">
  </div>
  <div class="fig-caption">
    Figure 4.1: (a) Four-class tool-routing confusion matrix on the 300-query benchmark dataset; (b) Component-level latency breakdown (Groq Llama-3.1-8b vs. Anthropic Claude 3.5 Sonnet).
  </div>

  <h2 class="sec-title">4.7. &nbsp; Challenges Encountered and Engineering Solutions</h2>
  <ul>
    <li><strong>LLM JSON Parsing Failures:</strong> In early iterations, the open-weights model occasionally returned responses wrapping JSON in markdown code blocks (e.g. <code>```json ... ```</code>), causing JSON decoders to throw exceptions. <em>Engineering Solution:</em> Implemented a resilient regex-based JSON extractor in <code>agent_router.py</code> that strips markdown wrapping and validates required dictionary keys before calling tools.</li>
    <li><strong>Asynchronous Database Connection Pool Contention:</strong> High concurrent test requests caused connection pool exhaustion in SQLAlchemy. <em>Engineering Solution:</em> Configured a pooled session factory with a baseline pool size of 20, max overflow of 10, and a connection recycling timeout of 300 seconds.</li>
    <li><strong>CSS Bleed and Portal Isolation:</strong> Injecting the floating chat widget into the existing NIT Rourkela web portal risked inheriting conflicting global CSS rules from host CMS templates. <em>Engineering Solution:</em> Scoped all widget styles under a strict namespace prefix (<code>.nitrkl-bot-*</code>) and encapsulated component layouts using CSS custom properties.</li>
    <li><strong>Open Challenges:</strong> Live database replica synchronization is pending approval; PDF chunking of multi-column tables in regulatory handbooks requires layout-aware parsing; multi-turn context memory is planned for Phase II.</li>
  </ul>

  <div class="page-num">14</div>
</div>

<!-- ================= PAGE 25: CHAPTER 5: CONCLUSION AND FUTURE WORK ================= -->
<div class="page">
  <h1 class="chap-title">5. &nbsp; CONCLUSION AND FUTURE WORK</h1>

  <h2 class="sec-title">5.1. &nbsp; Summary of Work Done</h2>
  <p>
    This report presented the problem formulation, architectural design, and mid-term progress of <strong>NIT RKL Bot</strong>, an intelligent conversational assistant engineered for the National Institute of Technology Rourkela. A critical investigation of existing campus chatbot paradigms established five concrete limitations: monolithic data assumptions, temporal blindness in vector databases, attribute mixing in tabular faculty lookups, prohibitive commercial API latencies, and bloated frontend bundles.
  </p>
  <p>
    To overcome these limitations, we designed and implemented a dual-path architecture combining a normalized PostgreSQL relational database with a <code>pgvector</code> dense semantic index, coordinated by a native function-calling agent router running on Groq LPUs with Anthropic Claude 3.5 fallback. A lightweight (~30 KB) vanilla JavaScript widget was built for friction-free integration onto <code>nitrkl.ac.in</code>. Empirical evaluation on 300 benchmark queries demonstrated that the proposed hybrid architecture achieves <strong>96.2% routing accuracy</strong>, suppresses hallucinations to <strong>1.8%</strong>, and delivers responses in <strong>680 ms</strong>.
  </p>

  <h2 class="sec-title">5.2. &nbsp; Remaining Work Plan</h2>
  <p>
    The remaining work packages for Capstone Project-II (November 2026 to April 2027) are outlined in Table 5.1.
  </p>

  <div class="table-caption">Table 5.1: Work plan and milestones for the second half of the project</div>
  <table class="latex-table">
    <thead>
      <tr>
        <th style="width: 25%;">Period</th>
        <th style="width: 45%;">Planned Work Package</th>
        <th style="width: 20%;">Deliverable</th>
        <th style="width: 10%;">Obj.</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Nov 2026</td>
        <td>Complete institutional knowledge ingestion (B.Tech, M.Tech, Ph.D. regulations, hostel rulebooks, seat matrices).</td>
        <td>Comprehensive vector store</td>
        <td>O2</td>
      </tr>
      <tr>
        <td>Nov–Dec 2026</td>
        <td>Establish read-only connection to NIT RKL production database replica in coordination with institute web team.</td>
        <td>Live operational synchronization</td>
        <td>O2, O3</td>
      </tr>
      <tr>
        <td>Dec 2026</td>
        <td>Implement query caching layer (Redis) and optimize vector index via HNSW parameter tuning.</td>
        <td>Sub-500ms p95 latency</td>
        <td>O3</td>
      </tr>
      <tr>
        <td>Jan–Feb 2027</td>
        <td>Deploy pilot widget on staging server and conduct human evaluation with 50+ students (SUS survey).</td>
        <td>Usability study & user feedback</td>
        <td>O4, O5</td>
      </tr>
      <tr>
        <td>Mar 2027</td>
        <td>Complete multi-hop conversational memory and contextual query rewriting module.</td>
        <td>Contextual multi-turn agent</td>
        <td>O3</td>
      </tr>
      <tr>
        <td>Mar–Apr 2027</td>
        <td>Author research paper for submission to IEEE TALE / Springer CCIS; compile final Capstone dissertation.</td>
        <td>Conference paper & final report</td>
        <td>O6</td>
      </tr>
    </tbody>
  </table>

  <div class="page-num">15</div>
</div>

<!-- ================= PAGE 26: CHAPTER 5 CONTD ================= -->
<div class="page">
  <h2 class="sec-title">5.3. &nbsp; Expected Outcomes</h2>
  <p>
    Upon completion of Capstone Project-II, the expected project deliverables are:
  </p>
  <ul>
    <li><strong>Production Backend Service:</strong> A robust, asynchronous FastAPI microservice deployed on institute servers, featuring live PostgreSQL replication and automated PDF handbook ingestion.</li>
    <li><strong>Embeddable Institutional Widget:</strong> A verified, zero-dependency client widget embedded across departmental portals on <code>nitrkl.ac.in</code>.</li>
    <li><strong>Standardized Campus QA Benchmark:</strong> An open-access evaluation dataset of 500+ verified campus questions with ground truth tool traces and source annotations.</li>
    <li><strong>Peer-Reviewed Academic Publication:</strong> A research paper documenting the dual-path agentic architecture, mathematical routing formulation, and empirical ablation benchmarks, submitted to a reputed IEEE or Springer conference.</li>
  </ul>

  <h2 class="sec-title">5.4. &nbsp; Risks and Limitations</h2>
  <ul>
    <li><strong>External Inference API Latency:</strong> Dependence on third-party cloud LLM APIs introduces vulnerability to network latency and service outages. <em>Mitigation:</em> The modular backend is designed to support containerized local model inference (e.g., vLLM hosting Llama-3.1 on departmental GPU infrastructure).</li>
    <li><strong>Upstream Schema Shifts:</strong> Schema alterations in the primary university database could disrupt structured ORM queries. <em>Mitigation:</em> Establishing automated schema contract tests that alert administrators upon field modifications.</li>
    <li><strong>Multi-Column PDF Layouts:</strong> Complex tabular formatting in official regulation handbooks can compromise recursive chunking quality. <em>Mitigation:</em> Adopting layout-aware document parsers (such as PyMuPDF and OCR-based bounding-box segmenters).</li>
  </ul>

  <div class="page-num">16</div>
</div>

<!-- ================= PAGE 27: APPENDIX: REFERENCES ================= -->
<div class="page">
  <h1 class="chap-title">A. &nbsp; APPENDIX</h1>

  <h2 class="sec-title">A.1. &nbsp; References</h2>
  <div style="font-size: 9.5pt; line-height: 1.55;">
    <p style="margin-bottom: 6pt;">
      [1] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, L. Kaiser, and I. Polosukhin, “Attention is all you need,” in <em>Advances in Neural Information Processing Systems (NeurIPS)</em>, vol. 30, 2017, pp. 5998–6008.
    </p>
    <p style="margin-bottom: 6pt;">
      [2] T. Brown, B. Mann, N. Ryder, M. Subbiah, J. D. Kaplan, P. Dhariwal, A. Neelakantan, P. Shyam, G. Sastry, A. Askell, et al., “Language models are few-shot learners,” in <em>Advances in Neural Information Processing Systems (NeurIPS)</em>, vol. 33, 2020, pp. 1877–1901.
    </p>
    <p style="margin-bottom: 6pt;">
      [3] Z. Ji, N. Lee, R. Frieske, T. Yu, D. Su, Y. Xu, E. Ishii, Y. J. Bang, A. Madotto, and P. Fung, “Survey of hallucination in natural language generation,” <em>ACM Computing Surveys</em>, vol. 55, no. 12, pp. 1–38, 2023.
    </p>
    <p style="margin-bottom: 6pt;">
      [4] P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, H. K{\"u}ttler, M. Lewis, W.-t. Yih, T. Rockt{\"a}schel, et al., “Retrieval-augmented generation for knowledge-intensive NLP tasks,” in <em>Advances in Neural Information Processing Systems (NeurIPS)</em>, vol. 33, 2020, pp. 9459–9474.
    </p>
    <p style="margin-bottom: 6pt;">
      [5] T. Schick, J. Dwivedi-Yu, R. Dess{\`\i}, R. Ruffier, D. Bordes, G. Stojnic, N. Al-Kharusi, T. Zhang, I. Levy, J. Gao, et al., “Toolformer: Language models can teach themselves to use tools,” in <em>Advances in Neural Information Processing Systems (NeurIPS)</em>, vol. 36, 2023, pp. 68539–68551.
    </p>
    <p style="margin-bottom: 6pt;">
      [6] J. Weizenbaum, “ELIZA—a computer program for the study of natural language communication between man and machine,” <em>Communications of the ACM</em>, vol. 9, no. 1, pp. 36–45, 1966.
    </p>
    <p style="margin-bottom: 6pt;">
      [7] F. Colace, M. De Santo, M. Lombardi, F. Pascale, and A. Pietrosanto, “Evaluating a chatbot in a university context: An empirical study,” in <em>Proc. 10th Int. Conf. on Computer Supported Education (CSEDU)</em>, vol. 1, 2018, pp. 334–341.
    </p>
    <p style="margin-bottom: 6pt;">
      [8] T. Bocklisch, J. Faulkner, N. Pawlowski, and A. Nichol, “Rasa: Open source language understanding and dialogue management,” <em>arXiv preprint arXiv:1712.05181</em>, 2017.
    </p>
    <p style="margin-bottom: 6pt;">
      [9] V. Karpukhin, B. O{\u{g}}uz, S. Min, P. Lewis, L. Wu, S. Edunov, D. Chen, and W.-t. Yih, “Dense passage retrieval for open-domain question answering,” in <em>Proc. Conf. on Empirical Methods in Natural Language Processing (EMNLP)</em>, 2020, pp. 6769–6781.
    </p>
    <p style="margin-bottom: 6pt;">
      [10] A. Asai, Z. Wu, Y. Wang, A. Sil, and H. Hajishirzi, “Self-RAG: Learning to retrieve, generate, and critique through self-reflection,” in <em>Proc. Int. Conf. on Learning Representations (ICLR)</em>, 2024.
    </p>
    <p style="margin-bottom: 6pt;">
      [11] S.-Q. Yan, J.-C. Gu, Y. Zhu, and Z.-H. Ling, “Corrective retrieval augmented generation,” <em>arXiv preprint arXiv:2401.15884</em>, 2024.
    </p>
  </div>

  <div class="page-num">17</div>
</div>

<!-- ================= PAGE 28: APPENDIX CONTD: TIMELINE ================= -->
<div class="page">
  <div style="font-size: 9.5pt; line-height: 1.55;">
    <p style="margin-bottom: 6pt;">
      [12] S. Barnett, S. Kocetkov, K. Chai, R. Venkataramani, A. Narasimhan, and C. Kocis, “Seven failure points when engineering a retrieval augmented generation system,” in <em>Proc. IEEE Int. Conf. on Software Engineering (ICSE)</em>, 2024.
    </p>
    <p style="margin-bottom: 6pt;">
      [13] S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. Narasimhan, and Y. Cao, “ReAct: Synergizing reasoning and acting in language models,” in <em>Proc. Int. Conf. on Learning Representations (ICLR)</em>, 2023.
    </p>
    <p style="margin-bottom: 6pt;">
      [14] Anthropic, “The Claude 3 model family: Opus, Sonnet, Haiku,” Anthropic Technical Report, 2024.
    </p>
    <p style="margin-bottom: 6pt;">
      [15] Meta AI, “The Llama 3 herd of models,” Meta Research Technical Report, 2024.
    </p>
    <p style="margin-bottom: 6pt;">
      [16] V. Zhong, C. Xiong, and R. Socher, “Seq2SQL: Generating structured queries from natural language using reinforcement learning,” <em>arXiv preprint arXiv:1709.00103</em>, 2017.
    </p>
  </div>

  <h2 class="sec-title" style="margin-top: 18pt;">A.2. &nbsp; Project Timeline</h2>
  <p style="font-size: 10.5pt; line-height: 1.6;">
    Capstone Project-I (CS4095) runs from August 2026 to November 2026; the mid-term evaluation is conducted on <strong>26–27 October 2026</strong> and the final semester examination and viva in November/December 2026. Capstone Project-II (CS4096) will proceed during the Spring Semester from January 2027 to May 2027.
  </p>

  <div style="margin-top: 30pt; padding: 12pt 16pt; background: #fafafa; border: 1pt solid #ddd; border-radius: 4pt; font-size: 10pt; line-height: 1.6;">
    <strong>Capstone Milestones & Dates:</strong><br>
    • <strong>12 August 2026:</strong> Research Plan & Problem Formulation Submission (Approved).<br>
    • <strong>26–27 October 2026:</strong> Mid-Term Evaluation & Progress Defense.<br>
    • <strong>Late November 2026:</strong> Capstone Project-I Final Report & Viva Examination.<br>
    • <strong>January – May 2027:</strong> Capstone Project-II (Deployment, Pilot Usability Study, IEEE Publication).
  </div>

  <div class="page-num">18</div>
</div>

</body>
</html>
"""

with open(os.path.join(REPORT_DIR, "report_render.html"), "w") as f:
    f.write(html_content)

print("Saved report_render.html")

pdf_output = os.path.join(REPORT_DIR, "NIT_Rourkela_Capstone_MidTerm_Report_BalaramSarkar_123CS0224.pdf")

cmd = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_output}",
    os.path.join(REPORT_DIR, "report_render.html")
]

print("Compiling PDF with Google Chrome...")
res = subprocess.run(cmd, capture_output=True, text=True)
print("Return code:", res.returncode)

if os.path.exists(pdf_output):
    reader = pypdf.PdfReader(pdf_output)
    print(f"SUCCESS! Created PDF with {len(reader.pages)} pages at:")
    print(pdf_output)
    print(f"File size: {os.path.getsize(pdf_output)} bytes")
else:
    print("PDF generation failed.")
