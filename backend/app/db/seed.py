"""
==============================================================================
File: backend/app/db/seed.py
Role: Institutional Database Seeder for NIT Rourkela Information System
Purpose: Populates comprehensive, production-ready NIT Rourkela institutional data:
         - notices (circulars, admissions, fees, library, placement)
         - faculty (deans, HODs, professors across all departments)
         - academic_calendar (milestones, exams, registrations, breaks, convocation)
         - events (Innovision, Nitrutsav, Vriddhi, HackNITR, TEDx, conferences)
         - hostels (all 10 Halls of Residence, wardens, curfews, facilities)
         - document_chunks (regulations, attendance, fee waivers with 384-d embeddings)
==============================================================================
"""

import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.connection import SessionLocal, engine
from app.db.models import Base, Notice, Faculty, AcademicCalendar, Event, Hostel, DocumentChunk
from app.pipeline.embeddings import encode_batch

logger = logging.getLogger("nitrkl_bot.db.seed")

# ------------------------------------------------------------------------------
# 1. Official Notices & Circulars (12 Detailed Notices)
# ------------------------------------------------------------------------------
SEED_NOTICES = [
    {
        "title": "Autumn Semester Registration 2026-27 Notice",
        "category": "Academic",
        "published_date": datetime(2026, 7, 15, 10, 0),
        "department": "Academic Office",
        "content_summary": "Online fee payment and ERP subject registration for all continuing B.Tech, M.Tech, and Ph.D students begins July 20, 2026. Late registration with penalty starts July 29.",
        "pdf_url": "https://www.nitrkl.ac.in/Academics/Notices/Autumn2026Reg.pdf"
    },
    {
        "title": "B.Tech Physical Reporting & Document Verification (JoSAA / CSAB 2026)",
        "category": "Admission",
        "published_date": datetime(2026, 7, 28, 9, 30),
        "department": "Admissions Office",
        "content_summary": "Newly admitted 1st year B.Tech candidates must physically report at the Student Activity Centre (SAC) between August 10-14, 2026 with original certificates, medical fitness proof, and fee receipts.",
        "pdf_url": "https://www.nitrkl.ac.in/Admissions/JoSAA2026ReportingSchedule.pdf"
    },
    {
        "title": "Hall of Residence Room Allotment for 1st Year Undergraduates (2026-27)",
        "category": "Hostel",
        "published_date": datetime(2026, 8, 2, 14, 0),
        "department": "Chief Warden Office",
        "content_summary": "Room allocation list for 1st year B.Tech students published. Boys are allotted M.S. Swaminathan (MSS) Hall and girls to C.V. Raman (CVR) Hall. Motor vehicles strictly prohibited for 1st-year students.",
        "pdf_url": "https://www.nitrkl.ac.in/StudentLife/HallsOfResidence/Allotment2026.pdf"
    },
    {
        "title": "Phase-1 Campus Placement Season: Registration for Final Year Students",
        "category": "Placement",
        "published_date": datetime(2026, 8, 5, 11, 0),
        "department": "Training & Placement Centre",
        "content_summary": "Pre-placement talks and aptitude assessments for graduating B.Tech/M.Tech batches begin August 22. All eligible students must upload verified resumes on the T&P portal.",
        "pdf_url": "https://www.nitrkl.ac.in/Placement/TPO_Phase1_Guidelines.pdf"
    },
    {
        "title": "Tuition Fee Waiver Application Guidelines for Academic Year 2026-27",
        "category": "Fee",
        "published_date": datetime(2026, 7, 18, 16, 0),
        "department": "Academic & Accounts",
        "content_summary": "Eligible candidates seeking full tuition fee waiver (family income < Rs 1.0 Lakh or SC/ST/PwD) or 2/3rd waiver (family income Rs 1.0-5.0 Lakhs) must submit verified income certificates before August 15.",
        "pdf_url": "https://www.nitrkl.ac.in/Academics/FeeWaiver2026.pdf"
    },
    {
        "title": "Biju Pattnaik Central Library: Extended 24/7 Hours during Mid-Sem Exams",
        "category": "General",
        "published_date": datetime(2026, 9, 12, 10, 0),
        "department": "Central Library",
        "content_summary": "The main reading room and digital library terminal section will remain open 24 hours daily from September 18 to September 28 to support mid-semester exam revisions.",
        "pdf_url": "https://www.nitrkl.ac.in/Library/ExamHoursCircular.pdf"
    },
    {
        "title": "Postgraduate (M.Tech) GATE Assistantship Disbursal Notice",
        "category": "Academic",
        "published_date": datetime(2026, 8, 20, 15, 0),
        "department": "Academic Office",
        "content_summary": "Regular M.Tech scholars with valid GATE scores receive monthly HTRA stipend of Rs. 12,400 subject to maintaining minimum 6.5 CPI and 8 hours weekly departmental teaching assistance.",
        "pdf_url": "https://www.nitrkl.ac.in/Academics/PG_GATE_Stipend_Notice.pdf"
    },
    {
        "title": "National Scholarship Portal (NSP) & State MCM Scholarship Verification",
        "category": "Scholarship",
        "published_date": datetime(2026, 8, 25, 12, 0),
        "department": "Dean Student Welfare Office",
        "content_summary": "Students applying for National Scholarship Portal (NSP) and state post-matric schemes must submit biometric authentication and original income proofs at Student Activity Centre Room 104.",
        "pdf_url": "https://www.nitrkl.ac.in/StudentWelfare/NSP_Verification_2026.pdf"
    },
    {
        "title": "Summer Internship & Industrial Training NOC Guidelines 2027",
        "category": "Academic",
        "published_date": datetime(2026, 10, 5, 14, 30),
        "department": "Training & Placement Centre",
        "content_summary": "Pre-final year undergraduate students seeking No Objection Certificates (NOC) for summer industrial internships (May-July) must apply through ERP portal endorsed by Department HOD.",
        "pdf_url": "https://www.nitrkl.ac.in/Placement/Summer_Internship_NOC_Guidelines.pdf"
    },
    {
        "title": "24th Annual Convocation: Degree Application, Dress Code & Gown Distribution",
        "category": "Academic",
        "published_date": datetime(2026, 12, 10, 11, 0),
        "department": "Academic Office",
        "content_summary": "Graduating B.Tech, M.Tech, M.Sc, MBA, and Ph.D recipients must register online for in-person conferment of degrees at Biju Pattnaik Auditorium. Traditional handloom dress code compulsory.",
        "pdf_url": "https://www.nitrkl.ac.in/Convocation/Convocation2027_Notice.pdf"
    },
    {
        "title": "Student Activity Centre (SAC): Club Orientations & Technical Society Recruitment",
        "category": "Event",
        "published_date": datetime(2026, 8, 18, 17, 0),
        "department": "Student Activity Centre",
        "content_summary": "Induction drives for technical, cultural, film/music, and literary societies commence August 24 at SAC grounds and LA complexes. Open to all newly admitted 1st year students.",
        "pdf_url": "https://www.nitrkl.ac.in/StudentLife/SAC_Inductions_2026.pdf"
    },
    {
        "title": "Institute Health Centre: 24/7 Medical Care & Compulsory Student Insurance",
        "category": "General",
        "published_date": datetime(2026, 8, 8, 10, 0),
        "department": "Health Centre",
        "content_summary": "Campus health dispensary provides round-the-clock emergency medical consultations, ambulance transport (+91-661-246-2140), and cashless referrals to CWS Hospital and Ispat General Hospital (IGH).",
        "pdf_url": "https://www.nitrkl.ac.in/HealthCentre/Medical_Advisory_2026.pdf"
    }
]

# ------------------------------------------------------------------------------
# 2. Comprehensive Faculty Directory (Institute Leadership, Deans & HODs)
# ------------------------------------------------------------------------------
SEED_FACULTY = [
    # Institute Leadership & Deans
    {
        "name": "Prof. K. Umamaheshwar Rao",
        "designation": "Director & Professor",
        "department": "Mining Engineering",
        "is_hod": False,
        "email": "director@nitrkl.ac.in",
        "phone": "+91-661-246-2001",
        "office_location": "Director Office, Administrative Building",
        "research_interests": "Rock Mechanics, Environmental Management in Mines, Underground Space Technology"
    },
    {
        "name": "Prof. S. K. Patel",
        "designation": "Dean (Academic) & Professor",
        "department": "Mechanical Engineering",
        "is_hod": False,
        "email": "dean-ac@nitrkl.ac.in",
        "phone": "+91-661-246-2010",
        "office_location": "Dean Academic Office, Administrative Building",
        "research_interests": "Thermal Engineering, Heat Transfer, Fluid Dynamics"
    },
    {
        "name": "Prof. Sidhartha S. Jena",
        "designation": "Dean (Student Welfare) & Professor",
        "department": "Civil Engineering",
        "is_hod": False,
        "email": "dean-sw@nitrkl.ac.in",
        "phone": "+91-661-246-2020",
        "office_location": "Student Activity Centre (SAC) 1st Floor",
        "research_interests": "Structural Engineering, Concrete Technology, Disaster Mitigation"
    },
    {
        "name": "Prof. Kunal Pal",
        "designation": "Chief Warden (Halls of Residence) & Professor",
        "department": "Biotechnology and Medical Engineering",
        "is_hod": False,
        "email": "chiefwarden@nitrkl.ac.in",
        "phone": "+91-661-246-2100",
        "office_location": "Chief Warden Office, Near SAC Complex",
        "research_interests": "Biomedical Instrumentation, Biomaterials, Drug Delivery"
    },

    # Computer Science and Engineering (CSE)
    {
        "name": "Prof. K. C. Pati",
        "designation": "Professor & Head of Department (HOD)",
        "department": "Computer Science and Engineering",
        "is_hod": True,
        "email": "hod-cs@nitrkl.ac.in",
        "phone": "+91-661-246-2350",
        "office_location": "Department of CSE, Main Academic Building Room 210",
        "research_interests": "High Performance Computing, Parallel Algorithms, Theoretical Computer Science"
    },
    {
        "name": "Prof. B. Majhi",
        "designation": "Professor",
        "department": "Computer Science and Engineering",
        "is_hod": False,
        "email": "bmajhi@nitrkl.ac.in",
        "phone": "+91-661-246-2352",
        "office_location": "CSE Building Room 215",
        "research_interests": "Image Processing, Soft Computing, Cyber Security, Pattern Recognition"
    },
    {
        "name": "Prof. Pankaj Kumar Sa",
        "designation": "Associate Professor",
        "department": "Computer Science and Engineering",
        "is_hod": False,
        "email": "pksa@nitrkl.ac.in",
        "phone": "+91-661-246-2358",
        "office_location": "CSE Building Room 218",
        "research_interests": "Computer Vision, Biometrics, Deep Learning, Video Surveillance"
    },
    {
        "name": "Prof. Ratnakar Dash",
        "designation": "Associate Professor",
        "department": "Computer Science and Engineering",
        "is_hod": False,
        "email": "rask@nitrkl.ac.in",
        "phone": "+91-661-246-2364",
        "office_location": "CSE Building Room 222",
        "research_interests": "Cloud Computing, Big Data Architectures, Machine Learning"
    },
    {
        "name": "Prof. Sambit Bakshi",
        "designation": "Associate Professor",
        "department": "Computer Science and Engineering",
        "is_hod": False,
        "email": "bakshisambit@nitrkl.ac.in",
        "phone": "+91-661-246-2368",
        "office_location": "CSE Building Room 224",
        "research_interests": "Biometric Authentication, Visual Privacy, Multimedia Security"
    },

    # Electronics and Communication Engineering (ECE)
    {
        "name": "Prof. S. Meher",
        "designation": "Professor & Head of Department (HOD)",
        "department": "Electronics and Communication Engineering",
        "is_hod": True,
        "email": "hod-ec@nitrkl.ac.in",
        "phone": "+91-661-246-2450",
        "office_location": "ECE Building Room 301",
        "research_interests": "Digital Signal Processing, VLSI Design, Speech & Audio Processing"
    },
    {
        "name": "Prof. K. K. Mahapatra",
        "designation": "Professor",
        "department": "Electronics and Communication Engineering",
        "is_hod": False,
        "email": "kkm@nitrkl.ac.in",
        "phone": "+91-661-246-2455",
        "office_location": "ECE Building Room 304",
        "research_interests": "Low Power VLSI, Embedded Systems, Semiconductor Devices"
    },
    {
        "name": "Prof. Poonam Singh",
        "designation": "Professor",
        "department": "Electronics and Communication Engineering",
        "is_hod": False,
        "email": "psingh@nitrkl.ac.in",
        "phone": "+91-661-246-2460",
        "office_location": "ECE Building Room 308",
        "research_interests": "Wireless Communications, 5G/6G Networks, MIMO Systems"
    },

    # Electrical Engineering (EE)
    {
        "name": "Prof. S. K. Das",
        "designation": "Professor & Head of Department (HOD)",
        "department": "Electrical Engineering",
        "is_hod": True,
        "email": "hod-ee@nitrkl.ac.in",
        "phone": "+91-661-246-2400",
        "office_location": "Electrical Engineering Dept Room 102",
        "research_interests": "Power Systems Engineering, Renewable Energy Integration, Smart Grids"
    },
    {
        "name": "Prof. B. Chitti Babu",
        "designation": "Associate Professor",
        "department": "Electrical Engineering",
        "is_hod": False,
        "email": "bcbabu@nitrkl.ac.in",
        "phone": "+91-661-246-2412",
        "office_location": "EE Dept Room 108",
        "research_interests": "Power Electronics, Microgrid Control, Solar PV Integration"
    },
    {
        "name": "Prof. Sanjeeb Kumar Kar",
        "designation": "Associate Professor",
        "department": "Electrical Engineering",
        "is_hod": False,
        "email": "skkar@nitrkl.ac.in",
        "phone": "+91-661-246-2418",
        "office_location": "EE Dept Room 114",
        "research_interests": "Electric Drives, High Voltage Engineering, Electric Vehicles"
    },

    # Mechanical Engineering (ME)
    {
        "name": "Prof. D. R. K. Parhi",
        "designation": "Professor & Head of Department (HOD)",
        "department": "Mechanical Engineering",
        "is_hod": True,
        "email": "hod-me@nitrkl.ac.in",
        "phone": "+91-661-246-2500",
        "office_location": "Mechanical Engineering Block Room 101",
        "research_interests": "Robotics, Mobile Manipulators, Finite Element Methods, Vibration Analysis"
    },
    {
        "name": "Prof. S. S. Mahapatra",
        "designation": "Professor",
        "department": "Mechanical Engineering",
        "is_hod": False,
        "email": "ssmahapatra@nitrkl.ac.in",
        "phone": "+91-661-246-2510",
        "office_location": "Mechanical Engineering Block Room 105",
        "research_interests": "CAD/CAM, Quality Engineering, Industrial Engineering"
    },
    {
        "name": "Prof. S. K. Sahoo",
        "designation": "Professor",
        "department": "Mechanical Engineering",
        "is_hod": False,
        "email": "sks@nitrkl.ac.in",
        "phone": "+91-661-246-2515",
        "office_location": "Mechanical Block Room 108",
        "research_interests": "Thermal Engineering, Fluid Mechanics, Turbomachinery"
    },

    # Civil Engineering (CE)
    {
        "name": "Prof. C. R. Patra",
        "designation": "Professor & Head of Department (HOD)",
        "department": "Civil Engineering",
        "is_hod": True,
        "email": "hod-ce@nitrkl.ac.in",
        "phone": "+91-661-246-2550",
        "office_location": "Civil Engineering Building Room 201",
        "research_interests": "Geotechnical Engineering, Soil Mechanics, Foundation Engineering"
    },
    {
        "name": "Prof. Mahabir Panda",
        "designation": "Professor",
        "department": "Civil Engineering",
        "is_hod": False,
        "email": "mpanda@nitrkl.ac.in",
        "phone": "+91-661-246-2555",
        "office_location": "Civil Engineering Building Room 205",
        "research_interests": "Transportation Engineering, Pavement Materials, Highway Engineering"
    },

    # Chemical Engineering (CH)
    {
        "name": "Prof. Pradip Chowdhury",
        "designation": "Professor & Head of Department (HOD)",
        "department": "Chemical Engineering",
        "is_hod": True,
        "email": "hod-ch@nitrkl.ac.in",
        "phone": "+91-661-246-2600",
        "office_location": "Chemical Engineering Block Room 104",
        "research_interests": "Adsorption Technology, Metal-Organic Frameworks (MOFs), Carbon Capture"
    },
    {
        "name": "Prof. R. K. Singh",
        "designation": "Professor",
        "department": "Chemical Engineering",
        "is_hod": False,
        "email": "rksingh@nitrkl.ac.in",
        "phone": "+91-661-246-2605",
        "office_location": "Chemical Block Room 108",
        "research_interests": "Biofuels, Pyrolysis, Polymer Degradation, Renewable Energy"
    },

    # Metallurgical and Materials Engineering (MM)
    {
        "name": "Prof. B. C. Ray",
        "designation": "Professor & Head of Department (HOD)",
        "department": "Metallurgical and Materials Engineering",
        "is_hod": True,
        "email": "hod-mm@nitrkl.ac.in",
        "phone": "+91-661-246-2700",
        "office_location": "Metallurgy Building Room 101",
        "research_interests": "Composite Materials, Environmental Degradation, Phase Transformations"
    },

    # Biotechnology and Medical Engineering (BM)
    {
        "name": "Prof. Subhankar Paul",
        "designation": "Professor & Head of Department (HOD)",
        "department": "Biotechnology and Medical Engineering",
        "is_hod": True,
        "email": "hod-bm@nitrkl.ac.in",
        "phone": "+91-661-246-2650",
        "office_location": "BM Engineering Building Room 102",
        "research_interests": "Tissue Engineering, Biomaterials, Biosensors, Cancer Nanotechnology"
    },

    # Mining Engineering (MN)
    {
        "name": "Prof. H. B. Sahu",
        "designation": "Professor & Head of Department (HOD)",
        "department": "Mining Engineering",
        "is_hod": True,
        "email": "hod-mn@nitrkl.ac.in",
        "phone": "+91-661-246-2750",
        "office_location": "Mining Dept Room 102",
        "research_interests": "Spontaneous Combustion of Coal, Mine Environment & Safety"
    },

    # Basic Sciences & Management
    {
        "name": "Prof. G. K. Panda",
        "designation": "Professor & Head of Department (HOD)",
        "department": "Department of Mathematics",
        "is_hod": True,
        "email": "hod-ma@nitrkl.ac.in",
        "phone": "+91-661-246-2800",
        "office_location": "Mathematics Dept Room 201",
        "research_interests": "Number Theory, Diophantine Equations, Optimization"
    },
    {
        "name": "Prof. D. Behera",
        "designation": "Professor & Head of Department (HOD)",
        "department": "Department of Physics",
        "is_hod": True,
        "email": "hod-ph@nitrkl.ac.in",
        "phone": "+91-661-246-2850",
        "office_location": "Physics Dept Room 105",
        "research_interests": "Condensed Matter Physics, High Temperature Superconductivity"
    },
    {
        "name": "Prof. R. K. Patel",
        "designation": "Professor & Head of Department (HOD)",
        "department": "Department of Chemistry",
        "is_hod": True,
        "email": "hod-cy@nitrkl.ac.in",
        "phone": "+91-661-246-2900",
        "office_location": "Chemistry Dept Room 102",
        "research_interests": "Environmental Chemistry, Water Fluoride Removal, Adsorption"
    },
    {
        "name": "Prof. Rajeev Kumar Panda",
        "designation": "Professor & Head of Department (HOD)",
        "department": "School of Management",
        "is_hod": True,
        "email": "hod-sm@nitrkl.ac.in",
        "phone": "+91-661-246-2950",
        "office_location": "School of Management Room 101",
        "research_interests": "Marketing Management, Consumer Behaviour, Services Marketing"
    }
]

# ------------------------------------------------------------------------------
# 3. Full Academic Calendar (Autumn & Spring 2026-27)
# ------------------------------------------------------------------------------
SEED_CALENDAR = [
    {
        "event_name": "Autumn Semester Registration Deadline",
        "category": "Registration",
        "start_date": datetime(2026, 7, 20),
        "end_date": datetime(2026, 7, 28),
        "target_audience": "All B.Tech, M.Tech, Ph.D",
        "description": "Online subject registration on ERP portal. Late registration with Rs. 2,000 fine till August 2."
    },
    {
        "event_name": "Commencement of Autumn Classes",
        "category": "Academic",
        "start_date": datetime(2026, 7, 29),
        "end_date": None,
        "target_audience": "All Students",
        "description": "Classroom instruction begins for all undergraduate and postgraduate batches."
    },
    {
        "event_name": "Mid-Semester Examinations (Autumn 2026)",
        "category": "Exam",
        "start_date": datetime(2026, 9, 20),
        "end_date": datetime(2026, 9, 26),
        "target_audience": "All B.Tech/M.Tech",
        "description": "Formal mid-term written examinations conducted in LA-1 and LA-2 lecture hall complexes."
    },
    {
        "event_name": "Durga Puja & Autumn Break Holidays",
        "category": "Holiday",
        "start_date": datetime(2026, 10, 18),
        "end_date": datetime(2026, 10, 25),
        "target_audience": "All",
        "description": "Institute and academic departments remain closed for Dussehra & Durga Puja holidays."
    },
    {
        "event_name": "End-Semester Theory & Practical Examinations (Autumn 2026)",
        "category": "Exam",
        "start_date": datetime(2026, 11, 23),
        "end_date": datetime(2026, 12, 4),
        "target_audience": "All Students",
        "description": "Final end-semester evaluations. Minimum 75% attendance required to receive admit card."
    },
    {
        "event_name": "Autumn Semester Grade Publication",
        "category": "Academic",
        "start_date": datetime(2026, 12, 14),
        "end_date": datetime(2026, 12, 14),
        "target_audience": "All Students",
        "description": "Publication of SGPA and CGPA results on ERP portal. Grade appeal window opens for 7 days."
    },
    {
        "event_name": "Winter Vacation",
        "category": "Holiday",
        "start_date": datetime(2026, 12, 5),
        "end_date": datetime(2026, 12, 31),
        "target_audience": "Undergraduate Students",
        "description": "Winter vacation for B.Tech students. Hostels remain open for research scholars."
    },
    {
        "event_name": "Spring Semester Registration 2027",
        "category": "Registration",
        "start_date": datetime(2027, 1, 2),
        "end_date": datetime(2027, 1, 5),
        "target_audience": "All Students",
        "description": "Course registration and fee payment for Spring 2026-27 semester on institute ERP."
    },
    {
        "event_name": "Commencement of Spring Classes 2027",
        "category": "Academic",
        "start_date": datetime(2027, 1, 6),
        "end_date": None,
        "target_audience": "All Students",
        "description": "Spring semester theory and laboratory instruction commences."
    },
    {
        "event_name": "24th Annual Convocation 2027",
        "category": "Academic",
        "start_date": datetime(2027, 1, 16),
        "end_date": datetime(2027, 1, 16),
        "target_audience": "Graduating Cohorts",
        "description": "Conferment of degrees at Biju Pattnaik Auditorium in presence of Chief Guest."
    },
    {
        "event_name": "Mid-Semester Examinations (Spring 2027)",
        "category": "Exam",
        "start_date": datetime(2027, 2, 22),
        "end_date": datetime(2027, 2, 28),
        "target_audience": "All Students",
        "description": "Mid-term examinations for Spring 2026-27 session."
    },
    {
        "event_name": "End-Semester Examinations (Spring 2027)",
        "category": "Exam",
        "start_date": datetime(2027, 4, 26),
        "end_date": datetime(2027, 5, 7),
        "target_audience": "All Students",
        "description": "Final end-semester evaluations for Spring semester."
    },
    {
        "event_name": "Summer Vacation & Summer Term Registration 2027",
        "category": "Academic",
        "start_date": datetime(2027, 5, 10),
        "end_date": datetime(2027, 7, 15),
        "target_audience": "Undergraduate Students",
        "description": "Summer break, industrial internships, and remedial summer term course registration."
    }
]

# ------------------------------------------------------------------------------
# 4. Campus Events & Fests
# ------------------------------------------------------------------------------
SEED_EVENTS = [
    {
        "title": "Innovision 2026 - Annual Techno-Management Fest",
        "organizer": "Student Activity Centre (SAC) - Technical Society",
        "venue": "Biju Pattnaik Auditorium & SAC Grounds",
        "event_date": datetime(2026, 11, 6, 9, 0),
        "description": "Eastern India's premier technical festival featuring robotics marathons, AI hackathons, drone racing, gaming, and guest lectures from industry luminaries."
    },
    {
        "title": "Vriddhi 2026 - All India Inter-NIT Sports Festival",
        "organizer": "Student Activity Centre (SAC) - Games & Sports Society",
        "venue": "Dilip Tirkey Stadium & Sachin Tendulkar Cricket Ground",
        "event_date": datetime(2026, 10, 30, 8, 0),
        "description": "National sports carnival hosting 20+ NITs competing across cricket, football, basketball, badminton, table tennis, and athletics."
    },
    {
        "title": "Nitrutsav 2027 - Annual Cultural Festival",
        "organizer": "SAC Cultural & Literary Society",
        "venue": "Biju Pattnaik Auditorium & DTS Open Air Theatre",
        "event_date": datetime(2027, 2, 12, 17, 0),
        "description": "Flagship 3-day cultural extravaganza with theatrical plays, battle of the bands, classical dance contests, fashion shows, and celebrity pro-nights."
    },
    {
        "title": "HackNITR 6.0 - Flagship 36-Hour Hackathon",
        "organizer": "OpenCode & GDSC NIT Rourkela",
        "venue": "Lecture Gallery LA-1",
        "event_date": datetime(2026, 10, 28, 10, 0),
        "description": "Major student hackathon connecting 500+ developers solving challenges in Web3, HealthTech, EdTech, and Sustainable AI with Rs. 5 Lakhs prize pool."
    },
    {
        "title": "International Conference on Smart Materials & Computing (ICSMC 2026)",
        "organizer": "Department of CSE & Physics",
        "venue": "TIIR Building Auditorium",
        "event_date": datetime(2026, 10, 12, 9, 30),
        "description": "IEEE-sponsored technical conference with paper presentations, keynote speeches from global researchers, and workshops on quantum computing."
    },
    {
        "title": "TEDxNITRourkela 2027 - Ideas Worth Spreading",
        "organizer": "Literary & Cultural Society",
        "venue": "Biju Pattnaik Auditorium",
        "event_date": datetime(2027, 1, 24, 10, 0),
        "description": "Independently organized TED event hosting thought leaders, scientists, entrepreneurs, and social innovators."
    },
    {
        "title": "Multi-Ethnic Festival 2027",
        "organizer": "SAC Cultural Society",
        "venue": "Open Air Theatre (OAT)",
        "event_date": datetime(2027, 3, 20, 18, 0),
        "description": "Celebration of regional diversity, traditional culinary feasts, folk dances, and cultural unity across all Indian states."
    }
]

# ------------------------------------------------------------------------------
# 5. Halls of Residence (All 10 Hostels)
# ------------------------------------------------------------------------------
SEED_HOSTELS = [
    {
        "name": "M. S. Swaminathan Hall of Residence (MSS)",
        "code": "MSS",
        "gender": "Boys",
        "warden": "Prof. B. C. Ray",
        "assistant_warden": "Prof. S. R. Patel",
        "contact_email": "warden-mss@nitrkl.ac.in",
        "curfew_time": "10:30 PM (9:30 PM for 1st Year UG students)",
        "description": "Dedicated residence for 1st year B.Tech undergraduate boys. Equipped with sports courts, centralized dining mess, study library, Wi-Fi, and 24/7 security."
    },
    {
        "name": "Vikram Sarabhai Hall of Residence (VS)",
        "code": "VS",
        "gender": "Boys",
        "warden": "Prof. S. K. Pratihar",
        "assistant_warden": "Prof. A. K. Sahoo",
        "contact_email": "warden-vs@nitrkl.ac.in",
        "curfew_time": "10:30 PM",
        "description": "Undergraduate senior boys hall with single and double occupancy rooms, gym, indoor badminton court, music room, and cooperative cafeteria."
    },
    {
        "name": "Homi Bhabha Hall of Residence (HB)",
        "code": "HB",
        "gender": "Boys",
        "warden": "Prof. R. K. Patel",
        "assistant_warden": "Prof. N. K. Sharma",
        "contact_email": "warden-hb@nitrkl.ac.in",
        "curfew_time": "10:30 PM",
        "description": "Hall of residence for 2nd and 3rd year undergraduate boys with active student council, garden lawns, volleyball court, and dining hall."
    },
    {
        "name": "Shanti Swaroop Bhatnagar Hall of Residence (SSB)",
        "code": "SSB",
        "gender": "Boys",
        "warden": "Prof. S. K. Sahoo",
        "assistant_warden": "Prof. P. K. Ray",
        "contact_email": "warden-ssb@nitrkl.ac.in",
        "curfew_time": "10:30 PM",
        "description": "Senior undergraduate boys and dual degree students hostel with library, reading room, sports facilities, and mess."
    },
    {
        "name": "Satish Dhawan Hall of Residence (SD)",
        "code": "SD",
        "gender": "Boys",
        "warden": "Prof. K. K. Khatua",
        "assistant_warden": "Prof. M. K. Mohanty",
        "contact_email": "warden-sd@nitrkl.ac.in",
        "curfew_time": "10:30 PM",
        "description": "Senior undergraduate boys hostel featuring single rooms, gym, basketball court, and late-night cafeteria."
    },
    {
        "name": "G. D. Birla Hall of Residence (GDB)",
        "code": "GDB",
        "gender": "Boys",
        "warden": "Prof. U. C. Pati",
        "assistant_warden": "Prof. T. K. Dan",
        "contact_email": "warden-gdb@nitrkl.ac.in",
        "curfew_time": "10:30 PM",
        "description": "Undergraduate boys hall with active recreational club, green lawns, and hygienic mess dining."
    },
    {
        "name": "Dhirubhai Ambani Hall of Residence (DBA)",
        "code": "DBA",
        "gender": "Boys",
        "warden": "Prof. S. K. Behera",
        "assistant_warden": "Prof. D. K. Biswal",
        "contact_email": "warden-dba@nitrkl.ac.in",
        "curfew_time": "10:30 PM",
        "description": "Dedicated modern hall of residence for M.Tech, M.Sc, and Ph.D research scholars with single rooms, reading lounge, and night canteen."
    },
    {
        "name": "C. V. Raman Hall of Residence (CVR)",
        "code": "CVR",
        "gender": "Girls",
        "warden": "Prof. S. Mohanty",
        "assistant_warden": "Prof. M. K. Jena",
        "contact_email": "warden-cvr@nitrkl.ac.in",
        "curfew_time": "10:30 PM (9:30 PM for 1st Year UG students)",
        "description": "Primary residence for undergraduate girls (all 1st year and senior cohorts). Equipped with round-the-clock female security personnel, biometric check-in, beauty parlour, gym, and dining mess."
    },
    {
        "name": "Kiran Mazumdar Shaw Hall of Residence (KMS)",
        "code": "KMS",
        "gender": "Girls",
        "warden": "Prof. Archana Mallik",
        "assistant_warden": "Prof. P. Tripathy",
        "contact_email": "warden-kms@nitrkl.ac.in",
        "curfew_time": "10:30 PM",
        "description": "Senior undergraduate girls and postgraduate scholars hall of residence with quiet study zones, Wi-Fi connectivity, and hygienic mess."
    },
    {
        "name": "Sarojini Naidu Hall of Residence (SN)",
        "code": "SN",
        "gender": "Girls",
        "warden": "Prof. Smrutirekha Sahoo",
        "assistant_warden": "Prof. Lopamudra Giri",
        "contact_email": "warden-sn@nitrkl.ac.in",
        "curfew_time": "10:30 PM",
        "description": "Dedicated hall of residence for postgraduate women, M.Tech, and Ph.D scholars with air-conditioned reading room and single occupancy rooms."
    }
]

# ------------------------------------------------------------------------------
# 6. Detailed Document Chunks for RAG Vector Store (12 Comprehensive Regulations)
# ------------------------------------------------------------------------------
SEED_DOCUMENT_CHUNKS = [
    {
        "document_name": "B.Tech Academic Regulations Handbook",
        "category": "Academic Rules",
        "chunk_index": 0,
        "content": (
            "Clause 4.2 Attendance Policy: Every undergraduate student must maintain a minimum attendance of 75% in each registered "
            "theory and practical course to be eligible to appear in the End-Semester examinations. A student whose attendance falls "
            "between 65% and 74% may apply for medical condonation to the Dean (Academic) within 7 days of returning to campus, "
            "accompanied by an authorized hospital certificate. Students with attendance below 65% are categorically disqualified "
            "from the final examination and awarded an 'F' grade, necessitating repeating the course when offered next."
        ),
        "chunk_metadata": {"section": "Clause 4.2 - Attendance & Condonation", "page": 14}
    },
    {
        "document_name": "B.Tech Academic Regulations Handbook",
        "category": "Academic Rules",
        "chunk_index": 1,
        "content": (
            "Clause 6.1 CGPA and Degree Requirements: Evaluation is conducted on a 10-point grading scale (Ex=10, A=9, B=8, C=7, D=6, P=5, F=0). "
            "To qualify for the award of the B.Tech degree, a student must successfully earn all prescribed credits (typically 160-165 credits) "
            "and obtain a minimum cumulative grade point average (CGPA) of 6.0 without any pending backlogs, 'F', or 'I' (Incomplete) grades. "
            "Semester Grade Point Average (SGPA) is computed as the weighted sum of credit-points divided by the total registered credits."
        ),
        "chunk_metadata": {"section": "Clause 6.1 - Grading & Graduation Criteria", "page": 22}
    },
    {
        "document_name": "B.Tech Academic Regulations Handbook",
        "category": "Academic Rules",
        "chunk_index": 2,
        "content": (
            "Clause 8.3 Change of Branch/Discipline: A student admitted to B.Tech through JoSAA/CSAB may be permitted to change branch at the "
            "end of the 1st year (2nd semester). Eligibility requirements: (a) Student must have cleared all credits prescribed in 1st and 2nd "
            "semesters in the first attempt without any backlogs. (b) Minimum CGPA at the end of 2nd semester must be 8.50 or higher (8.00 for SC/ST). "
            "(c) Branch change will not be granted if department strength falls below 85% or exceeds 110% of sanctioned intake. "
            "(d) Students involved in disciplinary actions or ragging are ineligible."
        ),
        "chunk_metadata": {"section": "Clause 8.3 - Branch Change Regulations", "page": 29}
    },
    {
        "document_name": "Hall of Residence Conduct Rules & Guidelines",
        "category": "Hostel Rules",
        "chunk_index": 0,
        "content": (
            "Hostel Entry Timings & Curfews: All residents must return to their respective Halls of Residence before 10:30 PM every night. "
            "For first-year undergraduate students, a strict entry curfew of 9:30 PM is enforced. Leaving the hostel after curfew hours is strictly "
            "prohibited except under medical emergency authorized by the Warden. Any overnight absence from campus requires prior approval through "
            "an online Night Pass signed by the Warden. Unreported overnight absences will incur a disciplinary fine of Rs. 1,000 and parent notification."
        ),
        "chunk_metadata": {"section": "Hostel Timings & Night Passes", "page": 6}
    },
    {
        "document_name": "Hall of Residence Conduct Rules & Guidelines",
        "category": "Hostel Rules",
        "chunk_index": 1,
        "content": (
            "Vehicle Restrictions & Anti-Ragging Measures: Motorized two-wheelers (scooters, motorcycles) and four-wheelers are strictly banned "
            "for all first-year B.Tech students inside the campus and hostel premises. First-year boarders are encouraged to use bicycles. "
            "Ragging in any form—physical, verbal, or mental—is a criminal offense under Supreme Court guidelines. The institute enforces zero tolerance. "
            "Instances can be reported anonymously to the Anti-Ragging Cell (+91-661-246-2020) or Chief Warden Office."
        ),
        "chunk_metadata": {"section": "Hostel Vehicles & Anti-Ragging", "page": 9}
    },
    {
        "document_name": "NIT Rourkela Fee Structure & Scholarship Policies",
        "category": "Fees & Scholarships",
        "chunk_index": 0,
        "content": (
            "Tuition Fee Structure and Exemption Schemes: The standard tuition fee for general/OBC undergraduate students is Rs. 62,500 per semester. "
            "Fee Waivers: (1) 100% full tuition fee waiver is granted to all SC, ST, and PwD category students. (2) 100% full tuition fee waiver is "
            "granted to economically backward students whose parental annual income is less than Rs. 1.0 Lakh. (3) 2/3rd tuition fee remission "
            "(paying only Rs. 20,833) applies to students whose annual family income is between Rs. 1.0 Lakh and Rs. 5.0 Lakhs. "
            "Income certificates issued by a competent state authority (Tahasildar / Revenue Officer) must be submitted annually."
        ),
        "chunk_metadata": {"section": "Tuition Fee Waivers", "page": 4}
    },
    {
        "document_name": "M.Tech & Ph.D Academic Ordinances",
        "category": "Postgraduate Regulations",
        "chunk_index": 0,
        "content": (
            "Half-Time Research Assistantship (HTRA) for PG Scholars: Regular M.Tech students admitted through CCMT with a valid GATE score "
            "are awarded an institute assistantship of Rs. 12,400 per month for a maximum of 24 months. To maintain eligibility, scholars must "
            "maintain a minimum CPI of 6.50 at the end of each semester and provide 8 hours per week of departmental teaching assistance "
            "(lab demonstrations, tutorial grading). Ph.D scholars receive JRF assistantship of Rs. 37,000 per month for the first two years, "
            "upgraded to SRF (Rs. 42,000/month) upon successful comprehensive assessment."
        ),
        "chunk_metadata": {"section": "HTRA Assistantship Rules", "page": 18}
    },
    {
        "document_name": "NIT Rourkela JoSAA / CSAB Admissions Handbook",
        "category": "Admissions",
        "chunk_index": 0,
        "content": (
            "Physical Reporting & Document Verification: All candidates allotted seats at NIT Rourkela through JoSAA/CSAB or DASA must complete "
            "in-person reporting at the Student Activity Centre (SAC). Required documentation includes: (1) Provisional Seat Allotment Letter, "
            "(2) JEE Main Admit Card & Rank Card, (3) Class 10 & 12 Board Marksheets, (4) Category/Caste Certificate (OBC-NCL/EWS issued after April 1), "
            "(5) State of Eligibility Certificate, (6) Medical Fitness Certificate in JoSAA format, and (7) Anti-ragging affidavit."
        ),
        "chunk_metadata": {"section": "JoSAA Physical Reporting", "page": 2}
    },
    {
        "document_name": "Biju Pattnaik Central Library Guide",
        "category": "Library Services",
        "chunk_index": 0,
        "content": (
            "Central Library Rules & Facilities: The BP Central Library houses over 85,000 print books and 10,000 e-journals. Normal operational "
            "hours are 8:00 AM to 10:00 PM on weekdays and 9:00 AM to 5:00 PM on weekends. During mid-sem and end-sem examinations, the air-conditioned "
            "reading room remains accessible 24 hours. Undergraduate students can borrow up to 6 books for a 15-day period using their RFID ID card. "
            "Digital library access provides IEEE Xplore, ScienceDirect, ACM Digital Library, and SpringerLink."
        ),
        "chunk_metadata": {"section": "Library Facilities", "page": 1}
    },
    {
        "document_name": "Training & Placement Centre (TPC) Policy Manual",
        "category": "Placements",
        "chunk_index": 0,
        "content": (
            "Placement Policy & Tiers: NIT Rourkela enforces a student-first 'One Student One Job' policy with Dream and Super Dream upgrade options. "
            "Tiers: Normal Job (up to 15 LPA), Dream Job (15 to 25 LPA), and Super Dream Job (greater than 25 LPA). Once a student secures a regular offer, "
            "they are eligible to participate only in Dream and Super Dream company drives. Pre-placement offers (PPOs) secured through summer internships "
            "must be formally accepted or rejected within 7 days of announcement. Minimum attendance of 80% is mandatory to participate in TPC drives."
        ),
        "chunk_metadata": {"section": "Placement Tiers & Dream Policy", "page": 5}
    },
    {
        "document_name": "Campus Health Centre Emergency & Dispensary Guide",
        "category": "Medical Services",
        "chunk_index": 0,
        "content": (
            "Health Centre Services & Medical Emergency: The on-campus Health Centre operates 24/7 with resident medical officers, emergency nursing staff, "
            "and an in-house pharmacy dispensing prescribed medicines free of charge to all enrolled students. Ambulance helpline (+91-661-246-2140) "
            "provides round-the-clock emergency transport to Community Welfare Society (CWS) Hospital and Ispat General Hospital (IGH). "
            "Every registered student is covered under the institute's compulsory group medical insurance policy."
        ),
        "chunk_metadata": {"section": "Health Centre Facilities", "page": 3}
    },
    {
        "document_name": "National and Institute Scholarship Guidelines",
        "category": "Scholarships",
        "chunk_index": 0,
        "content": (
            "Scholarships & Financial Assistance Schemes: (1) Institute Merit-cum-Means (MCM) Scholarship: Awarded to top 25% students of each branch "
            "with parental income < Rs. 4.5 Lakhs, providing monthly stipend and tuition waiver. (2) Foundation for Excellence (FFE) Scholarship: "
            "Provides financial assistance of Rs. 50,000 per year for brilliant students from low-income families. (3) Post-Matric State Scholarships "
            "(PRERANA for Odisha, Medhashree, NSP): Fully verified and authenticated through the Dean (Student Welfare) Office."
        ),
        "chunk_metadata": {"section": "Scholarship Schemes", "page": 8}
    }
]


def seed_database(force: bool = False) -> None:
    """
    Populates database tables with rich NIT Rourkela records.
    If force=True, clears existing records to prevent duplicates and rebuilds vector index.
    """
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        notice_count = db.query(Notice).count()
        if notice_count > 0 and not force:
            logger.info("Database is already seeded with records. Skipping seed.")
            return

        if force:
            logger.info("Force flag detected: Purging existing records for fresh institutional seed...")
            db.query(Notice).delete()
            db.query(Faculty).delete()
            db.query(AcademicCalendar).delete()
            db.query(Event).delete()
            db.query(Hostel).delete()
            db.query(DocumentChunk).delete()
            db.commit()

        logger.info("Seeding updated NIT Rourkela institutional database tables...")

        # 1. Seed Notices
        for item in SEED_NOTICES:
            db.add(Notice(**item))
        logger.info(f"Seeded {len(SEED_NOTICES)} Notices.")

        # 2. Seed Faculty
        for item in SEED_FACULTY:
            db.add(Faculty(**item))
        logger.info(f"Seeded {len(SEED_FACULTY)} Faculty profiles.")

        # 3. Seed Calendar
        for item in SEED_CALENDAR:
            db.add(AcademicCalendar(**item))
        logger.info(f"Seeded {len(SEED_CALENDAR)} Academic Calendar milestones.")

        # 4. Seed Events
        for item in SEED_EVENTS:
            db.add(Event(**item))
        logger.info(f"Seeded {len(SEED_EVENTS)} Campus Events.")

        # 5. Seed Hostels
        for item in SEED_HOSTELS:
            db.add(Hostel(**item))
        logger.info(f"Seeded {len(SEED_HOSTELS)} Halls of Residence.")

        # 6. Seed Document Chunks with dense embeddings
        chunk_texts = [c["content"] for c in SEED_DOCUMENT_CHUNKS]
        logger.info(f"Generating 384-dimensional dense vector embeddings for {len(chunk_texts)} chunks...")
        embeddings = encode_batch(chunk_texts)

        for idx, item in enumerate(SEED_DOCUMENT_CHUNKS):
            chunk = DocumentChunk(
                document_name=item["document_name"],
                category=item["category"],
                chunk_index=item["chunk_index"],
                content=item["content"],
                embedding=embeddings[idx] if idx < len(embeddings) else None,
                chunk_metadata=item["chunk_metadata"]
            )
            db.add(chunk)
        logger.info(f"Seeded {len(SEED_DOCUMENT_CHUNKS)} Document Chunks with dense embeddings.")

        db.commit()
        logger.info("Institutional database seeding completed successfully!")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


def seed_database_if_empty() -> None:
    """Helper invoked automatically during application startup."""
    seed_database(force=False)


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    force_flag = "--force" in sys.argv
    seed_database(force=force_flag)
