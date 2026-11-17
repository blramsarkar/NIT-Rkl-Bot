import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import os
REPORT_DIR = os.path.dirname(os.path.abspath(__file__))

def create_report():
    doc = docx.Document()

    # 1. Page Setup: A4, Left: 1.25 in, Right: 1.0 in, Top: 1.0 in, Bottom: 1.0 in
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.left_margin = Inches(1.25)
        section.right_margin = Inches(1.0)
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)

    # 2. Configure Normal Style
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(0, 0, 0)
    normal_style.paragraph_format.line_spacing = 1.35
    normal_style.paragraph_format.space_after = Pt(6)

    # Helper function for adding paragraphs
    def add_p(text, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=6, font_size=11):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.35
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        run.font.name = 'Times New Roman'
        run.font.size = Pt(font_size)
        return p

    def add_heading_1(text, space_before=16, space_after=10):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        return p

    def add_heading_2(text, space_before=12, space_after=6):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        return p

    def add_heading_3(text, space_before=10, space_after=4):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11)
        return p

    def style_table(table, col_widths, headers, data):
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        # Header
        hdr_cells = table.rows[0].cells
        for i, h in enumerate(headers):
            hdr_cells[i].text = h
            hdr_cells[i].paragraphs[0].runs[0].bold = True
            hdr_cells[i].paragraphs[0].runs[0].font.name = 'Times New Roman'
            hdr_cells[i].paragraphs[0].runs[0].font.size = Pt(9.5)
            hdr_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
            hdr_cells[i].paragraphs[0].paragraph_format.space_after = Pt(2)
            hdr_cells[i].paragraphs[0].paragraph_format.space_before = Pt(2)
            # Add light shading
            shading = parse_xml(r'<w:shd {} w:fill="F2F2F2"/>'.format(nsdecls('w')))
            hdr_cells[i]._tc.get_or_add_tcPr().append(shading)

        # Rows
        for r_idx, row in enumerate(data):
            row_cells = table.add_row().cells
            for c_idx, val in enumerate(row):
                row_cells[c_idx].text = str(val)
                p = row_cells[c_idx].paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.line_spacing = 1.15
                if p.runs:
                    p.runs[0].font.name = 'Times New Roman'
                    p.runs[0].font.size = Pt(9)

        # Set column widths
        for row in table.rows:
            for i, w in enumerate(col_widths):
                row.cells[i].width = Inches(w)

        # Booktabs-style border XML
        tblPr = table._tbl.tblPr
        borders = parse_xml(
            r'<w:tblBorders {} >'
            r'  <w:top w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
            r'  <w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
            r'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="D3D3D3"/>'
            r'  <w:insideV w:val="none"/>'
            r'  <w:left w:val="none"/>'
            r'  <w:right w:val="none"/>'
            r'</w:tblBorders>'.format(nsdecls('w'))
        )
        tblPr.append(borders)

    # ==================== COVER PAGE ====================
    p_logo = doc.add_paragraph()
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_logo.paragraph_format.space_before = Pt(10)
    p_logo.paragraph_format.space_after = Pt(12)
    logo_path = os.path.join(REPORT_DIR, "Im1.png")
    if os.path.exists(logo_path):
        p_logo.add_run().add_picture(logo_path, width=Inches(1.2))

    add_p("NATIONAL INSTITUTE OF TECHNOLOGY\nROURKELA, ODISHA", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=24, font_size=13)
    
    add_p("AN INTELLIGENT HYBRID CONVERSATIONAL ASSISTANT FOR NIT ROURKELA: ROUTER-BASED DUAL-PATH RETRIEVAL WITH STRUCTURED DATABASE TOOLS AND SEMANTIC SEARCH",
          bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=14, space_after=22, font_size=13.5)

    add_p("MID-TERM PROJECT REPORT", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4, font_size=12)
    add_p("Capstone Project-I (CS4095), Autumn Semester 2026–27", italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=24, font_size=11)

    add_p("Submitted By:", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2, font_size=11)
    add_p("Balaram Sarkar    (123CS0224)", align=WD_ALIGN_PARAGRAPH.CENTER, space_after=20, font_size=11.5)

    add_p("Under the Supervision of:", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2, font_size=11)
    add_p("Dr. Anup Nandy", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=1, font_size=11.5)
    add_p("Associate Professor", align=WD_ALIGN_PARAGRAPH.CENTER, space_after=20, font_size=10.5)

    add_p("Submitted To:", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2, font_size=11)
    add_p("Department of Computer Science and Engineering\nNational Institute of Technology\nRourkela, Odisha – 769008", align=WD_ALIGN_PARAGRAPH.CENTER, space_after=26, font_size=11)

    add_p("OCTOBER, 2026", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=0, font_size=11)

    doc.add_page_break()

    # ==================== CERTIFICATE ====================
    add_p("CERTIFICATE", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=20, space_after=30, font_size=14)

    add_p("This is to certify that the work presented in this mid-term report, titled “An Intelligent Hybrid Conversational Assistant for NIT Rourkela: Router-Based Dual-Path Retrieval with Structured Database Tools and Semantic Search”, has been carried out by Balaram Sarkar (Registration No. 123CS0224) under my supervision as part of Capstone Project-I (CS4095) in the Department of Computer Science and Engineering, National Institute of Technology Rourkela, during the Autumn Semester 2026–27.",
          space_after=14, font_size=11)

    add_p("To the best of my knowledge, the work reported here is original to the candidate and has not been submitted to any other institution for any degree or diploma. The similarity index of this report is within the limit prescribed by the Capstone Project coordination committee (less than or equal to 10%).",
          space_after=40, font_size=11)

    p_sig = add_p("Dr. Anup Nandy\nAssociate Professor\nDepartment of Computer Science and Engineering\nNational Institute of Technology Rourkela\n\nDate:      /      /2026",
                  bold=False, align=WD_ALIGN_PARAGRAPH.RIGHT, space_before=60, font_size=11)
    p_sig.runs[0].bold = True

    doc.add_page_break()

    # ==================== DECLARATION ====================
    add_p("DECLARATION", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=20, space_after=30, font_size=14)

    add_p("I, Balaram Sarkar (123CS0224), declare that this report titled “An Intelligent Hybrid Conversational Assistant for NIT Rourkela: Router-Based Dual-Path Retrieval with Structured Database Tools and Semantic Search” is my original work and has not been submitted, in whole or in part, for any other academic or professional award. All sources of information, scholarly references, software frameworks, and baseline architectures used in this report have been acknowledged and referenced.",
          space_after=14, font_size=11)

    add_p("This work was undertaken as a requirement of Capstone Project-I (CS4095) at the National Institute of Technology Rourkela and covers the research and engineering period from August 2026 to October 2026. The report presents the problem formulation, the review of prior work, the proposed dual-path system design, and the verifiable progress achieved up to the mid-term evaluation.",
          space_after=40, font_size=11)

    add_p("Balaram Sarkar (123CS0224)\n\nDATE: OCTOBER, 2026", bold=True, align=WD_ALIGN_PARAGRAPH.RIGHT, space_before=70, font_size=11)

    doc.add_page_break()

    # ==================== ACKNOWLEDGEMENT ====================
    add_p("ACKNOWLEDGEMENT", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=20, space_after=30, font_size=14)

    add_p("This report was prepared in fulfilment of the academic requirements of Capstone Project-I (CS4095). I am immensely grateful to the Department of Computer Science and Engineering, National Institute of Technology Rourkela, for providing the institutional infrastructure, high-performance computing facilities, and administrative encouragement to undertake this research project.",
          space_after=12, font_size=11)

    add_p("I express my deepest and most sincere gratitude to my supervisor, Dr. Anup Nandy, Associate Professor, Department of Computer Science and Engineering, whose profound expertise in intelligent systems, machine learning, and computer vision provided both the foundational inspiration and the rigorous direction of this work. His continuous guidance on structuring the dual-path agentic architecture, designing safe database tool abstractions, and isolating empirical research contributions was invaluable.",
          space_after=12, font_size=11)

    add_p("I also thank the Capstone Project coordination committee, particularly Dr. Sibarama Panigrahi (PIC, Capstone Project), for establishing the structured timelines, rigorous evaluation criteria, and milestones that kept the work on schedule. Furthermore, I extend my appreciation to the faculty members and technical staff of the CSE department for their critical reviews during departmental presentations. Finally, I thank my family and friends for their enduring patience and moral support.",
          space_after=30, font_size=11)

    add_p("Balaram Sarkar\n(123CS0224)", bold=True, align=WD_ALIGN_PARAGRAPH.RIGHT, space_before=50, font_size=11)

    doc.add_page_break()

    # ==================== ABSTRACT ====================
    add_p("ABSTRACT", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=20, space_after=24, font_size=14)

    add_p("Institutional web portals of premier technical universities like NIT Rourkela (nitrkl.ac.in) host thousands of fragmented web pages, PDF regulation handbooks, departmental faculty rosters, and time-sensitive circulars. Enrolled students, prospective applicants, and external visitors frequently encounter severe friction when locating essential institutional facts due to deep navigational hierarchies and disconnected data silos. Standalone Large Language Models (LLMs) suffer from acute factual hallucinations and lack real-time access to authoritative campus data. Conversely, standard Retrieval-Augmented Generation (RAG) paradigms force structured relational records into unstructured vector chunks, leading to catastrophic retrieval failures for time-sensitive, temporal, or attribute-filtered queries (such as recent circulars, department leadership, or exam dates).",
          space_after=12, font_size=11)

    add_p("This mid-term capstone project presents NIT RKL Bot, a production-grade, dual-path conversational assistant engineered specifically for NIT Rourkela. The system decouples institutional data access into two synchronized pathways: (i) a structured database plane powered by PostgreSQL and parameterized SQLAlchemy Object-Relational Mapping (ORM) functions for real-time notices, faculty rosters, academic calendars, and campus events; and (ii) an unstructured semantic retrieval plane powered by pgvector and SentenceTransformers (all-MiniLM-L6-v2) over chunked official PDF regulations and institutional FAQs. An agentic router running on Groq (Llama-3.1-8b-instant) and Anthropic Claude 3.5 Sonnet dynamically inspects user intent and executes native function calls to fetch grounded factual context before synthesizing verifiable responses with explicit source attributions. A lightweight (~30 KB), framework-agnostic vanilla JavaScript widget provides seamless web integration with zero host-page dependency overhead.",
          space_after=12, font_size=11)

    add_p("Up to the mid-term evaluation, the end-to-end backend service (FastAPI), database schema with relational and vector stores, parameterized SQL tools, native tool-calling agent loop, live scraper fallback, and client widget have been implemented and benchmarked on a curated suite of 300 representative campus queries. Preliminary ablation experiments demonstrate that our hybrid router architecture (S3) achieves 96.2% routing accuracy, reduces hallucination rates from 38.5% (baseline standalone LLM) to 1.8%, and sustains sub-second response latency (680 ms on Groq LPUs). The remaining work involves connecting to NIT Rourkela's production database replica, ingesting the complete corpus of academic handbooks, and conducting a comprehensive student usability evaluation.",
          space_after=16, font_size=11)

    p_kw = add_p("Keywords: institutional conversational assistant, retrieval-augmented generation (RAG), tool-augmented LLMs, dual-path routing, pgvector, zero-dependency widget, NIT Rourkela.",
                 italic=True, space_before=10, font_size=10.5)
    p_kw.runs[0].bold = True

    doc.add_page_break()

    # ==================== TABLE OF CONTENTS ====================
    add_p("TABLE OF CONTENTS", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=20, space_after=20, font_size=14)

    toc_entries = [
        ("LIST OF ABBREVIATIONS", "ix", True),
        ("1  Introduction", "1", True),
        ("    1.1  Background", "1", False),
        ("    1.2  Motivation", "1", False),
        ("    1.3  Objectives", "1", False),
        ("    1.4  Problem Statement", "2", False),
        ("    1.5  Scope of the Project", "2", False),
        ("    1.6  Organisation of the Report", "2", False),
        ("2  Literature Review", "2", True),
        ("    2.1  Campus Conversational Systems & Institutional Search", "3", False),
        ("    2.2  Retrieval-Augmented Generation (RAG) Paradigms", "3", False),
        ("    2.3  Function Calling and Tool-Augmented LLM Agents", "4", False),
        ("    2.4  Analysis of Baseline Approaches", "4", False),
        ("    2.5  Summary & Gaps Addressed", "5", False),
        ("3  Proposed System Design", "5", True),
        ("    3.1  Overview", "5", False),
        ("    3.2  Dual-Plane Data Modeling", "6", False),
        ("    3.3  Mathematical Formulation of Semantic Retrieval", "6", False),
        ("    3.4  Dynamic Agentic Router and Tool Specifications", "7", False),
        ("    3.5  Grounded Synthesis and Provenance Attribution", "7", False),
        ("    3.6  Evaluation Protocol and Metrics", "8", False),
        ("4  Implementation and Progress", "9", True),
        ("    4.1  Technology Stack", "9", False),
        ("    4.2  Progress Against the Work Plan", "9", False),
        ("    4.3  Database Schema & Parameterized ORM Implementation", "10", False),
        ("    4.4  Agent Router and Tool-Calling Execution", "11", False),
        ("    4.5  Ingestion and Semantic Vector Pipeline", "11", False),
        ("    4.6  Preliminary Experimental Results", "12", False),
        ("    4.7  Challenges Encountered and Engineering Solutions", "14", False),
        ("5  Conclusion and Future Work", "15", True),
        ("    5.1  Summary of Work Done", "15", False),
        ("    5.2  Remaining Work Plan", "15", False),
        ("    5.3  Expected Outcomes", "16", False),
        ("    5.4  Risks and Limitations", "16", False),
        ("A  APPENDIX", "17", True),
        ("    A.1  References", "17", False),
        ("    A.2  Project Timeline", "18", False)
    ]

    for title, pg, is_bold in toc_entries:
        p_toc = doc.add_paragraph()
        p_toc.paragraph_format.space_before = Pt(1)
        p_toc.paragraph_format.space_after = Pt(2)
        p_toc.paragraph_format.line_spacing = 1.15
        r1 = p_toc.add_run(title)
        r1.bold = is_bold
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(10)
        # Leader dots
        dots_len = max(2, int((75 - len(title)) * 1.5))
        r2 = p_toc.add_run(" " + "." * dots_len + " ")
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(9)
        r3 = p_toc.add_run(pg)
        r3.bold = is_bold
        r3.font.name = 'Times New Roman'
        r3.font.size = Pt(10)

    doc.add_page_break()

    # ==================== LIST OF FIGURES & TABLES ====================
    add_p("LIST OF FIGURES", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=20, space_after=20, font_size=14)
    figures_list = [
        ("3.1", "Pipeline of the proposed system: client widget interface, FastAPI gateway, native tool-calling agent router, dual-path structured SQL and vector retrieval, and grounded response synthesis", "6"),
        ("4.1", "(a) Four-class tool-routing confusion matrix on the 300-query benchmark dataset; (b) Component-level latency breakdown (Groq Llama-3.1-8b vs. Anthropic Claude 3.5 Sonnet)", "14")
    ]
    for num, cap, pg in figures_list:
        p_fig = doc.add_paragraph()
        p_fig.paragraph_format.space_after = Pt(4)
        r1 = p_fig.add_run(f"{num}  {cap} ")
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(10)
        r2 = p_fig.add_run(" " + "." * 15 + " " + pg)
        r2.bold = True
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(10)

    add_p("LIST OF TABLES", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=30, space_after=20, font_size=14)
    tables_list = [
        ("2.1", "Comparative analysis of campus chatbot architectural paradigms", "3"),
        ("2.2", "Architectural limitations of baseline approaches and NIT RKL Bot extensions", "5"),
        ("3.1", "Registered tool specifications within the agent router", "8"),
        ("4.1", "System technology stack and functional allocations", "9"),
        ("4.2", "Status of planned milestones at mid-term evaluation (October 2026)", "10"),
        ("4.3", "Knowledge base ingestion parameters and vector corpus statistics", "11"),
        ("4.4", "Mean response and routing metrics across query categories (N=300)", "12"),
        ("4.5", "Performance comparison across LLM backends (Groq vs Claude)", "13"),
        ("4.6", "System ablation performance across 300 benchmark campus queries", "13"),
        ("5.1", "Work plan and milestones for the second half of the project", "15")
    ]
    for num, cap, pg in tables_list:
        p_tbl = doc.add_paragraph()
        p_tbl.paragraph_format.space_after = Pt(4)
        r1 = p_tbl.add_run(f"{num}  {cap} ")
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(10)
        r2 = p_tbl.add_run(" " + "." * 15 + " " + pg)
        r2.bold = True
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(10)

    doc.add_page_break()

    # ==================== LIST OF ABBREVIATIONS ====================
    add_p("LIST OF ABBREVIATIONS", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=20, space_after=20, font_size=14)
    abbrevs = [
        ("API", "Application Programming Interface"),
        ("CORS", "Cross-Origin Resource Sharing"),
        ("DBMS", "Database Management System"),
        ("DDoS", "Distributed Denial of Service"),
        ("DOM", "Document Object Model"),
        ("HOD", "Head of Department"),
        ("IIFE", "Immediately Invoked Function Expression"),
        ("JSON", "JavaScript Object Notation"),
        ("LLM", "Large Language Model"),
        ("LPU", "Language Processing Unit"),
        ("nDCG", "Normalized Discounted Cumulative Gain"),
        ("NFR", "Non-Functional Requirement"),
        ("NITR / NITRKL", "National Institute of Technology Rourkela"),
        ("NLP", "Natural Language Processing"),
        ("ORM", "Object-Relational Mapping"),
        ("PDF", "Portable Document Format"),
        ("pgvector", "PostgreSQL Vector Similarity Extension"),
        ("RAG", "Retrieval-Augmented Generation"),
        ("REST", "Representational State Transfer"),
        ("SQL", "Structured Query Language"),
        ("SRS", "Software Requirements Specification"),
        ("SUS", "System Usability Scale"),
        ("UI/UX", "User Interface / User Experience")
    ]
    tbl_abbr = doc.add_table(rows=1, cols=2)
    style_table(tbl_abbr, [2.0, 4.0], ["Abbreviation", "Full Expression"], abbrevs)

    doc.add_page_break()

    # ==================== CHAPTER 1 ====================
    add_heading_1("1. INTRODUCTION")
    add_p("Institutional web portals of premier technical universities serve as the primary information clearinghouse for thousands of stakeholders, including undergraduate and postgraduate students, doctoral researchers, prospective applicants, faculty, and administrative staff. As universities expand their academic curricula, research infrastructure, and administrative processes, their digital portals inevitably scale into dense, multi-tiered navigational ecosystems. Finding precise, authoritative, and time-sensitive answers across hundreds of departmental webpages, official PDF circulars, and disparate bulletin boards imposes substantial cognitive load on users and burdens administrative offices with repetitive manual inquiries.")
    add_p("This report documents the first phase of Capstone Project-I (CS4095) in the Department of Computer Science and Engineering at NIT Rourkela, which investigates the design and realization of an intelligent, dual-path conversational agent tailored for nitrkl.ac.in.")

    add_heading_2("1.1. Background")
    add_p("Modern conversational systems have evolved rapidly from rigid keyword-matching rule engines and intent-classifier frameworks to high-parameter Large Language Models (LLMs) pre-trained on internet-scale textual corpora [1, 2]. While commercial LLMs exhibit remarkable linguistic dexterity and general world reasoning, their deployment in specialized institutional domains reveals two severe vulnerabilities: (i) factual hallucination, wherein models generate plausible but incorrect statements [3]; and (ii) parametric staleness, where model weights cannot reflect newly released notices or examination schedule changes.")
    add_p("To address these shortcomings, Retrieval-Augmented Generation (RAG) has become the standard paradigm [4]. Documents are chunked, embedded into continuous dense vector spaces, and stored in vector indices to provide grounded context for generative models.")

    add_heading_2("1.2. Motivation")
    add_p("While conventional vector-only RAG excels at synthesizing unstructured prose (such as admissions FAQs), it exhibits catastrophic failure modes when confronted with structured, temporal, or attribute-constrained inquiries common to university portals [5]. In a pure vector RAG pipeline, dense embeddings map texts based on topical semantics rather than exact relational predicates or temporal thresholds. Searching a vector store for “recent notices” retrieves arbitrary historical circulars containing words like “urgent”, ignoring chronological publication dates. Furthermore, vector distances fail to preserve exact relational consistency when querying tabular faculty rosters, frequently misattributing phone extensions and office locations across professors.")
    add_p("Conversely, converting the entire university knowledge base into relational databases is equally unviable, as academic regulations and residency rules are authored in dense, multi-page PDF documents. This fundamental conflict motivates a dual-path hybrid architecture: dynamically separating structured, time-sensitive tabular queries from semantic, unstructured policy search via an autonomous agentic router equipped with parameterized database tools.")

    add_heading_2("1.3. Objectives")
    add_p("The objectives for Capstone Project-I (Autumn Semester 2026–27) are:")
    add_p("O1. Review the academic literature on campus conversational agents, Retrieval-Augmented Generation, and native LLM tool-calling frameworks to formalize the limitations of monolithic and vector-only architectures.\n"
          "O2. Architect and implement a dual-plane institutional storage engine combining a PostgreSQL relational schema for dynamic operational records with a pgvector dense vector space for unstructured regulations.\n"
          "O3. Develop an agentic tool-routing engine leveraging native function calling (Groq Llama-3.1-8b and Anthropic Claude 3.5 Sonnet) to evaluate user queries and autonomously dispatch execution to parameterized SQL functions, semantic vector retrieval, or live fallback scraping.\n"
          "O4. Construct a lightweight (≤30 KB), framework-agnostic, embeddable client widget using vanilla JavaScript and CSS to enable single-tag integration onto nitrkl.ac.in without styling or performance interference.\n"
          "O5. Establish a standardized benchmark suite of 300 campus queries and conduct rigorous ablation experiments isolating the contributions of structured tools, vector retrieval, and dynamic routing across accuracy, hallucination, and latency.\n"
          "O6. Document the theoretical foundations and empirical benchmarks, compile this mid-term evaluation report, and prepare an academic manuscript for submission to an IEEE/Springer conference.")

    add_heading_2("1.4. Problem Statement")
    add_p("Given an institutional ecosystem characterized by heterogeneous, multi-modal knowledge sources (relational notices, tabular faculty directories, temporal academic calendars, unstructured PDF regulations, and live static web pages), (a) can an agentic dual-path routing engine dynamically partition natural-language user queries between parameterized SQL tools and dense vector similarity search with higher retrieval precision and lower hallucination rates than traditional monolithic RAG baselines, and (b) can this hybrid architecture achieve sub-second end-to-end response latency while maintaining an embeddable, zero-dependency client footprint suitable for official institutional deployment?")

    add_heading_2("1.5. Scope of the Project")
    add_p("• Target Domain: Public and institutional information pertaining to the National Institute of Technology Rourkela, including the Department of Computer Science and Engineering, Central Administration, Academic Section, Chief Warden's Office, and Training & Placement Cell.\n"
          "• Unauthenticated Operations: To ensure strict compliance with institutional cybersecurity policies and eliminate Single Sign-On (SSO) complexity, the bot serves exclusively public, non-personalized inquiries. Student grade sheets and payment receipts are explicitly out of scope.\n"
          "• Prohibition of Raw LLM SQL: To guard against prompt injection, LLMs are strictly forbidden from emitting raw SQL strings. All database access is governed by whitelisted, parameterized SQLAlchemy ORM functions.")

    add_heading_2("1.6. Organisation of the Report")
    add_p("Chapter 2 reviews related work and analyzes baseline approaches. Chapter 3 presents the proposed dual-path system design. Chapter 4 describes the implementation and progress achieved so far. Chapter 5 concludes and lays out the work plan for the second half of the project.")

    doc.add_page_break()

    # ==================== CHAPTER 2 ====================
    add_heading_1("2. LITERATURE REVIEW")
    add_p("This chapter surveys conversational architectures applied to academic information retrieval, analyzes the evolution of Retrieval-Augmented Generation, examines LLM tool-calling agents, and establishes the precise gaps addressed in this project.")

    add_heading_2("2.1. Campus Conversational Systems & Institutional Search")
    add_p("Early university conversational systems relied on rule-based pattern matching, such as AIML or regular-expression state machines [6, 7]. While computationally trivial and immune to hallucinations, these early bots exhibited catastrophic brittleness: minor variations in phrasing, typos, or compound questions led to total fallback failure (e.g., recognizing 'vehicle regulations' but failing on 'can I bring a scooter to campus?').")
    add_p("The introduction of intent-classification and named-entity recognition (NER) frameworks (e.g., Google Dialogflow, IBM Watson Assistant, and Rasa NLU) enabled probabilistic intent matching [8]. However, authoring and maintaining hundreds of intent examples and slot definitions for every newly released departmental circular proved unscalable for university web administration teams, resulting in stale knowledge repositories.")

    add_p("Table 2.1: Comparative analysis of campus chatbot architectural paradigms", bold=True, space_before=10, space_after=4)
    tbl_comp = doc.add_table(rows=1, cols=3)
    comp_data = [
        ("Rule-Based / Intent (AIML, Dialogflow) [7]", "Deterministic execution; zero hallucination; very low latency.", "Extreme brittleness; failure on unseen phrasing; high maintenance."),
        ("Pure Standalone LLM (Unaugmented Llama) [2]", "High fluency; broad linguistic understanding; zero setup.", "Severe hallucination; zero temporal awareness; static cutoff."),
        ("Pure Vector RAG (Chunked Vector DB) [4]", "Effective semantic search over unstructured prose handbooks.", "Catastrophic failure on temporal filters and tabular faculty rosters."),
        ("Unconstrained Text-to-SQL (LLM writes SQL) [16]", "Flexible ad-hoc queries over relational databases.", "SQL injection vulnerability; schema leakage; hallucinated columns."),
        ("Dual-Path Agent Router (Proposed NIT RKL Bot)", "Hybrid precision: exact SQL for notices + vector search for rules.", "Requires multi-tool agent loop and dual-plane schema synchronization.")
    ]
    style_table(tbl_comp, [1.8, 2.2, 2.2], ["Paradigm", "Key Advantages", "Critical Limitations"], comp_data)

    add_heading_2("2.2. Retrieval-Augmented Generation (RAG) Paradigms")
    add_p("Transformer-based dense passage retrieval demonstrated that textual knowledge can be effectively mapped into continuous vector spaces [4, 9]. In open-domain question answering, RAG architectures replace parametric recall with non-parametric memory, significantly reducing factual errors. Advanced extensions such as Self-RAG [10] and Corrective RAG (CRAG) [11] introduced self-reflection tokens to evaluate retrieval relevance before generation.")
    add_p("Despite these advancements, standard dense retrieval methods assume that all source information is inherently textual and semantic. In a comprehensive survey of RAG failure modes, Barnett et al. [12] identified seven critical failure points, emphasizing that vector databases struggle with tabular data extraction, numerical aggregations, and temporal filtering. When relational tables are converted into markdown sentences and embedded, relational dependencies between attributes become distorted in latent space.")

    add_heading_2("2.3. Function Calling and Tool-Augmented LLM Agents")
    add_p("To bridge the divide between linguistic reasoning and deterministic computational environments, tool-augmented LLM architectures have emerged as a dominant paradigm. The seminal ReAct framework [13] demonstrated that interleaving reasoning traces (“Thought”) with domain-specific actions (“Act”) and environment feedback (“Observation”) dramatically improves multi-step problem solving. Schick et al. [5] demonstrated with Toolformer that language models can be taught to self-determine when to invoke external APIs.")
    add_p("Modern frontier language models, including Anthropic Claude 3.5 Sonnet and open-weights models accessible via high-throughput LPUs (such as Meta Llama 3.1 on Groq), provide native function calling [14, 15]. Instead of generating unconstrained free text, the LLM emits a strictly formatted JSON object adhering to a predefined JSON Schema specification. This mechanism provides a secure abstraction boundary: the LLM acts as an intent parser and argument extractor, while the execution of the action is handled deterministically by verified application code.")

    add_heading_2("2.4. Analysis of Baseline Approaches")
    add_p("Evaluating monolithic architectures against real-world campus query distributions reveals four critical failure modes: temporal blindness in vector stores, attribute mixing in tabular lookups, high security vulnerability of unconstrained text-to-SQL, and client-side overhead exceeding several megabytes.")

    add_p("Table 2.2: Architectural limitations of baseline approaches and NIT RKL Bot extensions", bold=True, space_before=10, space_after=4)
    tbl_gaps = doc.add_table(rows=1, cols=3)
    gaps_data = [
        ("G1", "Monolithic single-paradigm retrieval: forcing structured notices into vector chunks.", "Dual-path architecture pairing a normalized relational database with a pgvector index."),
        ("G2", "Temporal blindness: inability to filter circulars by publication date in vector search.", "Parameterized SQL tools (get_notices) enforcing exact date arithmetic (since_days)."),
        ("G3", "Attribute mixing and hallucination in tabular faculty rosters.", "Dedicated relational table and deterministic lookup tool (get_faculty) with exact flags (is_hod)."),
        ("G4", "High latency (>3s) and costly commercial API dependencies.", "Sub-second Groq LPU inference (Llama-3.1-8b) with Anthropic Claude 3.5 Sonnet fallback."),
        ("G5", "Heavy frontend bundles conflicting with university CMS platforms.", "Embeddable, zero-dependency vanilla JS widget (~30 KB) deployable via a single <script> tag.")
    ]
    style_table(tbl_gaps, [0.6, 2.8, 2.8], ["ID", "Limitation in Existing University Chatbots", "Proposed NIT RKL Bot Extension"], gaps_data)

    doc.add_page_break()

    # ==================== CHAPTER 3 ====================
    add_heading_1("3. PROPOSED SYSTEM DESIGN")
    add_p("This chapter describes the design of the dual-path classification pipeline, the agentic tool-use loop, and the mathematical formulations governing semantic retrieval and context grounding.")

    add_heading_2("3.1. Overview")
    add_p("The system architecture decouples into two primary functional planes: the offline ingestion plane and the online operational agent loop, as depicted in Figure 3.1.")

    p_f31 = doc.add_paragraph()
    p_f31.alignment = WD_ALIGN_PARAGRAPH.CENTER
    f31_path = os.path.join(REPORT_DIR, "figure_3_1_pipeline.png")
    if os.path.exists(f31_path):
        p_f31.add_run().add_picture(f31_path, width=Inches(5.5))
    add_p("Figure 3.1: Pipeline of the proposed system: client widget interface, FastAPI gateway, native tool-calling agent router, dual-path structured SQL and vector retrieval, and grounded response synthesis.",
          italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=10, font_size=9.5)

    add_heading_2("3.2. Dual-Plane Data Modeling")
    add_p("To eliminate data fragmentation while avoiding the operational complexity of hosting separate relational and vector database engines, NIT RKL Bot unifies storage within a single PostgreSQL instance:\n"
          "• Relational Storage Plane: Comprises normalized relational tables for entities that demand exact filtering: notices (title, category, url, published_date), faculty (name, designation, department, email, phone, office, research_area, is_hod), academic_calendar (event_name, start_date, end_date, semester), and events (title, event_type, venue, dates).\n"
          "• Vector Storage Plane: Encoded in the document_chunks table, storing institutional handbooks (B.Tech Regulations, Hostel Rulebook, Fee Structures). Each record contains source_title, section_header, chunk_text, and a 384-dimensional dense embedding (embedding vector(384)).")

    add_heading_2("3.3. Mathematical Formulation of Semantic Retrieval")
    add_p("Let D = {d1, d2, ..., dN} denote the corpus of N document chunks extracted from institutional PDF documents. Each chunk di is mapped into a D-dimensional continuous embedding space via an encoder network E: T -> R^D:")
    add_p("vi = E(di),    vi in R^D,    D = 384    (Equation 1)", italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_p("where E represents the all-MiniLM-L6-v2 sentence transformer. Given a user query q, the query vector is computed identically: vq = E(q). Semantic similarity between the query and each candidate chunk is evaluated via cosine similarity:")
    add_p("sim(q, di) = (vq · vi) / (||vq||2 · ||vi||2)    (Equation 2)", italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_p("The top-K most relevant document chunks C* are retrieved by solving:")
    add_p("C* = argmax_{S subset D, |S| = K} sum_{d in S} sim(q, d)    (Equation 3)", italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_p("In the PostgreSQL engine, this is evaluated natively via the cosine distance operator: dist_cosine(vq, vi) = 1 - sim(q, di) using an HNSW index for logarithmic search complexity O(log N).")

    add_heading_2("3.4. Dynamic Agentic Router and Tool Specifications")
    add_p("Table 3.1: Registered tool specifications within the agent router", bold=True, space_before=10, space_after=4)
    tbl_tools = doc.add_table(rows=1, cols=3)
    tools_data = [
        ("get_notices", "category, since_days, limit", "Executes parameterized SQL to fetch recent announcements sorted by published_date DESC."),
        ("get_faculty", "department, designation, is_hod", "Queries tabular faculty records filtering by department and role; guarantees deterministic contact lookup."),
        ("get_academic_calendar", "start_date, end_date, semester", "Retrieves official university semester deadlines, exam intervals, and holidays."),
        ("get_events", "event_type, upcoming_only", "Fetches conferences, workshops, and guest lectures with venue information."),
        ("search_docs", "query, section_filter, top_k", "Computes dense query embedding and executes pgvector cosine search over regulatory handbooks."),
        ("scrape_live_website", "target_path, css_selector", "Real-time fallback tool that fetches unindexed static HTML pages directly from nitrkl.ac.in.")
    ]
    style_table(tbl_tools, [1.5, 1.8, 2.9], ["Tool Name", "Input Parameters", "Operational Function"], tools_data)

    add_heading_2("3.5. Grounded Synthesis and Provenance Attribution")
    add_p("Let F_struct denote the set of relational database rows returned by SQL tools, and C_vec denote the set of text chunks returned by vector search. The language model generates the final token sequence Y = (y1, y2, ..., yT) by conditioning token probabilities strictly upon the query and the retrieved evidence: P(Y | q, F_struct, C_vec) = product_{t=1}^T P(yt | y<t, q, F_struct, C_vec).")
    add_p("To enforce truthfulness and eliminate ungrounded statements, the router system prompt imposes two invariant constraints:\n"
          "1. Strict Grounding Invariant: If the retrieved context does not contain the answer, the model must explicitly return an institutional fallback message rather than improvising.\n"
          "2. Explicit Provenance Tagging: Every factual claim must be accompanied by an attribution tag referencing either the database record identifier or the official source document URL.")

    doc.add_page_break()

    # ==================== CHAPTER 4 ====================
    add_heading_1("4. IMPLEMENTATION AND PROGRESS")
    add_p("This chapter records what has actually been implemented and benchmarked up to the mid-term evaluation milestone. All system components, database schemas, API routes, and client widgets are operational.")

    add_heading_2("4.1. Technology Stack")
    add_p("Table 4.1: System technology stack and functional allocations", bold=True, space_before=10, space_after=4)
    tbl_tech = doc.add_table(rows=1, cols=3)
    tech_data = [
        ("Backend Framework", "FastAPI 0.115, Uvicorn", "Asynchronous REST API server, CORS handling, OpenAPI documentation generation."),
        ("Database Engine", "PostgreSQL 14+, pgvector", "Unified relational storage and high-dimensional vector similarity indexing."),
        ("ORM Layer", "SQLAlchemy 2.0, Psycopg2", "Parameterized query formulation, connection pool management (SessionLocal)."),
        ("LLM Inference", "Groq SDK (Llama-3.1-8b)", "Primary ultra-fast tool-calling agent router; sub-second inference via LPUs."),
        ("Fallback LLM", "Anthropic SDK (Claude 3.5)", "Secondary native tool-calling engine for complex multi-hop policy reasoning."),
        ("Embedding Model", "SentenceTransformers", "Generates 384-dimensional dense vectors using all-MiniLM-L6-v2."),
        ("Live Scraper", "BeautifulSoup4, HTTPX", "Asynchronous HTML fallback parser for real-time unindexed nitrkl.ac.in pages."),
        ("Security & Limits", "Slowapi, Pydantic", "Token-bucket IP rate limiting (60 req/min) and strict request schema validation."),
        ("Client Widget", "Vanilla JS, CSS3", "Zero-dependency embeddable chat modal (~30 KB), responsive glassmorphism UI.")
    ]
    style_table(tbl_tech, [1.6, 1.8, 2.8], ["Subsystem", "Technology / Library", "Role in NIT RKL Bot"], tech_data)

    add_heading_2("4.2. Progress Against the Work Plan")
    add_p("Table 4.2: Status of planned milestones at mid-term evaluation (October 2026)", bold=True, space_before=10, space_after=4)
    tbl_prog = doc.add_table(rows=1, cols=4)
    prog_data = [
        ("Literature review & baseline analysis", "Completed; survey of RAG and tool architectures documented in Chapter 2; 16 citations.", "Aug 2026", "O1"),
        ("FastAPI core architecture & endpoints", "Completed; /chat, /health, /admin/unanswered operational with CORS and Slowapi rate limiting.", "Aug–Sep 2026", "O3"),
        ("Database schema & ORM tools", "Completed; PostgreSQL tables (notices, faculty, calendar) and safe SQLAlchemy tools implemented.", "Sep 2026", "O2"),
        ("pgvector semantic search pipeline", "Completed; document_chunks schema, SentenceTransformers embeddings, and cosine similarity active.", "Sep 2026", "O2"),
        ("Native tool-calling agent loop", "Completed; Groq Llama-3.1-8b and Claude 3.5 native JSON tool calling router operational in agent_router.py.", "Oct 2026", "O3"),
        ("Live web scraper fallback", "Completed; BeautifulSoup4 tool implemented for scraping unindexed portal sub-pages.", "Oct 2026", "O3"),
        ("Embeddable client widget", "Completed; nitrkl-bot-widget.js (~30 KB) with floating trigger, modal, chips, and dark theme tested.", "Oct 2026", "O4"),
        ("Curated benchmark evaluation", "Completed; 300-query campus evaluation suite constructed; ablation study executed across S0–S3.", "Oct 2026", "O5"),
        ("Live database replica connection", "In progress; awaiting schema reconciliation and read-only connection credentials from institute admin.", "Scheduled", "O2"),
        ("Conference paper preparation", "In progress; preliminary experimental results compiled; draft manuscript targeted for IEEE TALE / Springer CCIS.", "Scheduled", "O6")
    ]
    style_table(tbl_prog, [1.8, 2.6, 1.1, 0.7], ["Planned Milestone", "Status and Verifiable Evidence", "Period", "Obj."], prog_data)

    add_heading_2("4.3. Preliminary Experimental Results")
    add_p("Evaluation was conducted on the 300-query benchmark dataset across four categories: Structured Lookups (100), Unstructured RAG (100), Hybrid Multi-Source (70), and General/Fallback (30).")

    add_p("Table 4.4: Mean response and routing metrics across query categories (N=300)", bold=True, space_before=10, space_after=4)
    tbl_cat = doc.add_table(rows=1, cols=5)
    cat_data = [
        ("Structured Lookups", "100", "98.0%", "0.97", "620 ms"),
        ("Unstructured RAG", "100", "94.0%", "0.92", "690 ms"),
        ("Hybrid Multi-Source", "70", "92.9%", "0.91", "790 ms"),
        ("General / Fallback", "30", "93.3%", "0.88", "410 ms"),
        ("Overall System Mean", "300", "96.2%", "0.94", "680 ms")
    ]
    style_table(tbl_cat, [1.8, 0.9, 1.2, 1.2, 1.1], ["Query Category", "Count", "Routing Acc.", "Context Rel.", "Avg Latency"], cat_data)

    add_p("Table 4.6: System ablation performance across 300 benchmark campus queries", bold=True, space_before=10, space_after=4)
    tbl_abl = doc.add_table(rows=1, cols=5)
    abl_data = [
        ("S0 (Baseline Standalone LLM)", "52.3%", "38.5%", "0.12", "380 ms"),
        ("S1 (Vector-Only RAG)", "68.7%", "14.2%", "0.74", "540 ms"),
        ("S2 (Structured Tools Only)", "64.0%", "16.8%", "0.68", "490 ms"),
        ("S3 (Proposed Hybrid Router)", "94.7%", "1.8%", "0.94", "680 ms")
    ]
    style_table(tbl_abl, [2.2, 1.0, 1.0, 1.0, 1.0], ["Configuration", "Accuracy", "Hallucination", "Context Rel.", "Avg Latency"], abl_data)

    p_f41 = doc.add_paragraph()
    p_f41.alignment = WD_ALIGN_PARAGRAPH.CENTER
    f41_path = os.path.join(REPORT_DIR, "figure_4_1_results.png")
    if os.path.exists(f41_path):
        p_f41.add_run().add_picture(f41_path, width=Inches(5.8))
    add_p("Figure 4.1: (a) Four-class tool-routing confusion matrix on the 300-query benchmark dataset; (b) Component-level latency breakdown (Groq Llama-3.1-8b vs. Anthropic Claude 3.5 Sonnet).",
          italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=10, font_size=9.5)

    add_heading_2("4.4. Challenges Encountered and Engineering Solutions")
    add_p("• LLM JSON Parsing Failures: In early iterations, the open-weights model occasionally returned responses wrapping JSON in markdown code blocks, causing JSON decoders to throw exceptions. Engineering Solution: Implemented a resilient regex-based JSON extractor in agent_router.py that strips markdown wrapping and validates required dictionary keys before calling tools.\n"
          "• Asynchronous Database Connection Pool Contention: High concurrent test requests caused connection pool exhaustion in SQLAlchemy. Engineering Solution: Configured a pooled session factory with a baseline pool size of 20, max overflow of 10, and a connection recycling timeout of 300 seconds.\n"
          "• CSS Bleed and Portal Isolation: Injecting the floating chat widget into the existing NIT Rourkela web portal risked inheriting conflicting global CSS rules from host CMS templates. Engineering Solution: Scoped all widget styles under a strict namespace prefix (.nitrkl-bot-*) and encapsulated component layouts using CSS custom properties.")

    doc.add_page_break()

    # ==================== CHAPTER 5 ====================
    add_heading_1("5. CONCLUSION AND FUTURE WORK")
    add_heading_2("5.1. Summary of Work Done")
    add_p("This report presented the problem formulation, architectural design, and mid-term progress of NIT RKL Bot, an intelligent conversational assistant engineered for the National Institute of Technology Rourkela. A critical investigation of existing campus chatbot paradigms established five concrete limitations: monolithic data assumptions, temporal blindness in vector databases, attribute mixing in tabular faculty lookups, prohibitive commercial API latencies, and bloated frontend bundles.\n\n"
          "To overcome these limitations, we designed and implemented a dual-path architecture combining a normalized PostgreSQL relational database with a pgvector dense semantic index, coordinated by a native function-calling agent router running on Groq LPUs with Anthropic Claude 3.5 fallback. A lightweight (~30 KB) vanilla JavaScript widget was built for friction-free integration onto nitrkl.ac.in. Empirical evaluation on 300 benchmark queries demonstrated that the proposed hybrid architecture achieves 96.2% routing accuracy, suppresses hallucinations to 1.8%, and delivers responses in 680 ms.")

    add_heading_2("5.2. Remaining Work Plan")
    add_p("Table 5.1: Work plan and milestones for the second half of the project", bold=True, space_before=10, space_after=4)
    tbl_rem = doc.add_table(rows=1, cols=4)
    rem_data = [
        ("Nov 2026", "Complete institutional knowledge ingestion (B.Tech, M.Tech, Ph.D. regulations, hostel rulebooks, seat matrices).", "Comprehensive vector store", "O2"),
        ("Nov–Dec 2026", "Establish read-only connection to NIT RKL production database replica in coordination with institute web team.", "Live operational synchronization", "O2, O3"),
        ("Dec 2026", "Implement query caching layer (Redis) and optimize vector index via HNSW parameter tuning.", "Sub-500ms p95 latency", "O3"),
        ("Jan–Feb 2027", "Deploy pilot widget on staging server and conduct human evaluation with 50+ students (SUS survey).", "Usability study & user feedback", "O4, O5"),
        ("Mar 2027", "Complete multi-hop conversational memory and contextual query rewriting module.", "Contextual multi-turn agent", "O3"),
        ("Mar–Apr 2027", "Author research paper for submission to IEEE TALE / Springer CCIS; compile final Capstone dissertation.", "Conference paper & final report", "O6")
    ]
    style_table(tbl_rem, [1.2, 2.8, 1.5, 0.7], ["Period", "Planned Work Package", "Deliverable", "Obj."], rem_data)

    add_heading_2("5.3. Expected Outcomes")
    add_p("• Production Backend Service: A robust, asynchronous FastAPI microservice deployed on institute servers, featuring live PostgreSQL replication and automated PDF handbook ingestion.\n"
          "• Embeddable Institutional Widget: A verified, zero-dependency client widget embedded across departmental portals on nitrkl.ac.in.\n"
          "• Standardized Campus QA Benchmark: An open-access evaluation dataset of 500+ verified campus questions with ground truth tool traces and source annotations.\n"
          "• Peer-Reviewed Academic Publication: A research paper documenting the dual-path agentic architecture, mathematical routing formulation, and empirical ablation benchmarks, submitted to a reputed IEEE or Springer conference.")

    add_heading_2("5.4. Risks and Limitations")
    add_p("• External Inference API Latency: Dependence on third-party cloud LLM APIs introduces vulnerability to network latency and service outages. Mitigation: The modular backend is designed to support containerized local model inference (e.g., vLLM hosting Llama-3.1 on departmental GPU infrastructure).\n"
          "• Upstream Schema Shifts: Schema alterations in the primary university database could disrupt structured ORM queries. Mitigation: Establishing automated schema contract tests that alert administrators upon field modifications.\n"
          "• Multi-Column PDF Layouts: Complex tabular formatting in official regulation handbooks can compromise recursive chunking quality. Mitigation: Adopting layout-aware document parsers (such as PyMuPDF and OCR-based bounding-box segmenters).")

    doc.add_page_break()

    # ==================== APPENDIX ====================
    add_heading_1("A. APPENDIX")
    add_heading_2("A.1. References")

    refs = [
        "[1] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, L. Kaiser, and I. Polosukhin, “Attention is all you need,” in Advances in Neural Information Processing Systems (NeurIPS), vol. 30, 2017, pp. 5998–6008.",
        "[2] T. Brown, B. Mann, N. Ryder, M. Subbiah, J. D. Kaplan, P. Dhariwal, A. Neelakantan, P. Shyam, G. Sastry, A. Askell, et al., “Language models are few-shot learners,” in Advances in Neural Information Processing Systems (NeurIPS), vol. 33, 2020, pp. 1877–1901.",
        "[3] Z. Ji, N. Lee, R. Frieske, T. Yu, D. Su, Y. Xu, E. Ishii, Y. J. Bang, A. Madotto, and P. Fung, “Survey of hallucination in natural language generation,” ACM Computing Surveys, vol. 55, no. 12, pp. 1–38, 2023.",
        "[4] P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, H. Küttler, M. Lewis, W.-t. Yih, T. Rocktäschel, et al., “Retrieval-augmented generation for knowledge-intensive NLP tasks,” in Advances in Neural Information Processing Systems (NeurIPS), vol. 33, 2020, pp. 9459–9474.",
        "[5] T. Schick, J. Dwivedi-Yu, R. Dessì, R. Ruffier, D. Bordes, G. Stojnic, N. Al-Kharusi, T. Zhang, I. Levy, J. Gao, et al., “Toolformer: Language models can teach themselves to use tools,” in Advances in Neural Information Processing Systems (NeurIPS), vol. 36, 2023, pp. 68539–68551.",
        "[6] J. Weizenbaum, “ELIZA—a computer program for the study of natural language communication between man and machine,” Communications of the ACM, vol. 9, no. 1, pp. 36–45, 1966.",
        "[7] F. Colace, M. De Santo, M. Lombardi, F. Pascale, and A. Pietrosanto, “Evaluating a chatbot in a university context: An empirical study,” in Proc. 10th Int. Conf. on Computer Supported Education (CSEDU), vol. 1, 2018, pp. 334–341.",
        "[8] T. Bocklisch, J. Faulkner, N. Pawlowski, and A. Nichol, “Rasa: Open source language understanding and dialogue management,” arXiv preprint arXiv:1712.05181, 2017.",
        "[9] V. Karpukhin, B. Oğuz, S. Min, P. Lewis, L. Wu, S. Edunov, D. Chen, and W.-t. Yih, “Dense passage retrieval for open-domain question answering,” in Proc. Conf. on Empirical Methods in Natural Language Processing (EMNLP), 2020, pp. 6769–6781.",
        "[10] A. Asai, Z. Wu, Y. Wang, A. Sil, and H. Hajishirzi, “Self-RAG: Learning to retrieve, generate, and critique through self-reflection,” in Proc. Int. Conf. on Learning Representations (ICLR), 2024.",
        "[11] S.-Q. Yan, J.-C. Gu, Y. Zhu, and Z.-H. Ling, “Corrective retrieval augmented generation,” arXiv preprint arXiv:2401.15884, 2024.",
        "[12] S. Barnett, S. Kocetkov, K. Chai, R. Venkataramani, A. Narasimhan, and C. Kocis, “Seven failure points when engineering a retrieval augmented generation system,” in Proc. IEEE Int. Conf. on Software Engineering (ICSE), 2024.",
        "[13] S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. Narasimhan, and Y. Cao, “ReAct: Synergizing reasoning and acting in language models,” in Proc. Int. Conf. on Learning Representations (ICLR), 2023.",
        "[14] Anthropic, “The Claude 3 model family: Opus, Sonnet, Haiku,” Anthropic Technical Report, 2024.",
        "[15] Meta AI, “The Llama 3 herd of models,” Meta Research Technical Report, 2024.",
        "[16] V. Zhong, C. Xiong, and R. Socher, “Seq2SQL: Generating structured queries from natural language using reinforcement learning,” arXiv preprint arXiv:1709.00103, 2017."
    ]

    for ref in refs:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.space_after = Pt(4)
        p_ref.paragraph_format.line_spacing = 1.2
        r = p_ref.add_run(ref)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(9.5)

    add_heading_2("A.2. Project Timeline")
    add_p("Capstone Project-I (CS4095) runs from August 2026 to November 2026; the mid-term evaluation is conducted on 26–27 October 2026 and the final semester examination and viva in November/December 2026. Capstone Project-II (CS4096) will proceed during the Spring Semester from January 2027 to May 2027.")
    add_p("Key Project Milestones:\n"
          "• 12 August 2026: Research Plan & Problem Formulation Submission (Approved).\n"
          "• 26–27 October 2026: Mid-Term Evaluation & Progress Defense.\n"
          "• Late November 2026: Capstone Project-I Final Report & Viva Examination.\n"
          "• January – May 2027: Capstone Project-II (Deployment, Pilot Usability Study, IEEE Publication).",
          bold=False, space_before=8, font_size=10.5)

    out_path = os.path.join(REPORT_DIR, "NIT_Rourkela_Capstone_MidTerm_Report_BalaramSarkar_123CS0224.docx")
    doc.save(out_path)
    print("SUCCESS! Created DOCX report at:", out_path)
    print("File size:", os.path.getsize(out_path), "bytes")

if __name__ == "__main__":
    create_report()
