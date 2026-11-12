"""
SmartRecruit — Database Seed Script (corrected schema)
Run inside the backend container:
  docker exec smartrecruit-backend python seed.py
"""

from datetime import datetime, timezone, timedelta
from pymongo import MongoClient
from pwdlib import PasswordHash
import random, os

# ─── Connection ───────────────────────────────────────────────────────────────
MONGO_URI = os.getenv(
    "MONGODB_URI",
    "mongodb://smartrecruit_admin:YourStrongMongoPassword@mongodb:27017/smart_recruit?authSource=admin"
)
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client["smart_recruit"]

users_col    = db["users"]
cands_col    = db["candidates"]
recs_col     = db["recruiters"]
companies_col = db["companies"]
members_col  = db["company_members"]
jobs_col     = db["job_offers"]
apps_col     = db["applications"]

ph = PasswordHash.recommended()
def hp(pw): return ph.hash(pw)
def now(d=0): return datetime.now(timezone.utc) + timedelta(days=d)

# ─── Wipe ─────────────────────────────────────────────────────────────────────
print("🗑  Clearing collections...")
for c in [apps_col, jobs_col, members_col, companies_col, recs_col, cands_col, users_col]:
    c.delete_many({})

# ─── 1. Users ─────────────────────────────────────────────────────────────────
print("👤 Creating users...")

def insert_user(email, pw, full_name, role, days_ago=-60):
    doc = {
        "email": email.lower(),
        "hashed_password": hp(pw),
        "full_name": full_name,
        "role": role,
        "is_active": True,
        "created_at": now(days_ago),
        "updated_at": now(days_ago + random.randint(1, 10)),
    }
    return str(users_col.insert_one(doc).inserted_id)

admin_id = insert_user("admin@smartrecruit.io", "Admin@1234", "Alex Morgan", "admin", -120)

recruiter_specs = [
    ("sarah.chen@techcorp.io",   "Sarah Chen",      "Talent Acquisition Lead",  "+1-415-555-0192",  0),
    ("james.walker@novainc.com", "James Walker",    "Senior HR Manager",         "+44-20-7946-0958", 1),
    ("amira.hassan@dataflow.io", "Amira Hassan",    "Head of People",            "+971-50-123-4567", 2),
    ("lucas.dubois@skylab.fr",   "Lucas Dubois",    "Tech Recruiter",            "+33-1-42-00-00-00",3),
    ("priya.sharma@nexusai.in",  "Priya Sharma",    "Engineering Recruiter",     "+91-98765-43210",  4),
]
rec_ids = []
for email, name, title, phone, idx in recruiter_specs:
    rid = insert_user(email, "Recruiter@1234", name, "recruiter", random.randint(-90,-40))
    rec_ids.append(rid)

candidate_specs = [
    ("carlos.ruiz@gmail.com",     "Carlos Ruiz"),
    ("yuki.tanaka@outlook.com",   "Yuki Tanaka"),
    ("fatima.zahra@proton.me",    "Fatima Zahra"),
    ("noah.anderson@gmail.com",   "Noah Anderson"),
    ("elena.popescu@yahoo.com",   "Elena Popescu"),
    ("kwame.asante@gmail.com",    "Kwame Asante"),
    ("sophie.martin@gmail.com",   "Sophie Martin"),
    ("arjun.mehta@hotmail.com",   "Arjun Mehta"),
    ("isabelle.dumont@gmail.com", "Isabelle Dumont"),
    ("omar.khalil@gmail.com",     "Omar Khalil"),
]
cand_ids = []
for email, name in candidate_specs:
    cid = insert_user(email, "Candidate@1234", name, "candidate", random.randint(-60,-10))
    cand_ids.append(cid)

print(f"   ✓ 1 admin, {len(rec_ids)} recruiters, {len(cand_ids)} candidates")

# ─── 2. Recruiter profiles ────────────────────────────────────────────────────
print("💼 Creating recruiter profiles...")
for i, (email, name, title, phone, idx) in enumerate(recruiter_specs):
    recs_col.insert_one({
        "user_id": rec_ids[i],
        "full_name": name,
        "phone": phone,
        "job_title": title,
        "company_id": None,
        "created_at": now(-80),
        "updated_at": now(-5),
    })

# ─── 3. Candidate profiles ────────────────────────────────────────────────────
print("🎓 Creating candidate profiles...")
candidate_profiles = [
    {   # Carlos Ruiz
        "full_name": "Carlos Ruiz",
        "phone": "+1-415-555-0101",
        "location": "San Francisco, CA",
        "skills": ["React", "Node.js", "TypeScript", "MongoDB", "AWS"],
        "education": [{"degree": "BSc", "institution": "UC Berkeley", "field_of_study": "Computer Science", "graduation_year": 2020}],
        "experience": [
            {"position": "Software Engineer", "company": "StartupCo", "description": "Built full-stack features with React and Node.js", "years": 3},
            {"position": "Junior Developer", "company": "WebAgency", "description": "Frontend development with React", "years": 1},
        ],
    },
    {   # Yuki Tanaka
        "full_name": "Yuki Tanaka",
        "phone": "+81-90-1234-5678",
        "location": "Tokyo, Japan",
        "skills": ["Python", "PyTorch", "TensorFlow", "Scikit-learn", "NLP"],
        "education": [{"degree": "MSc", "institution": "University of Tokyo", "field_of_study": "Artificial Intelligence", "graduation_year": 2021}],
        "experience": [
            {"position": "ML Engineer", "company": "AI Research Lab", "description": "NLP model training and deployment", "years": 3},
            {"position": "Data Scientist", "company": "Analytics Firm", "description": "Predictive modeling with scikit-learn", "years": 2},
        ],
    },
    {   # Fatima Zahra
        "full_name": "Fatima Zahra",
        "phone": "+212-6-61-00-00-01",
        "location": "Casablanca, Morocco",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker"],
        "education": [{"degree": "BSc", "institution": "ENSIAS", "field_of_study": "Software Engineering", "graduation_year": 2021}],
        "experience": [
            {"position": "Backend Engineer", "company": "Fintech Morocco", "description": "REST APIs with FastAPI and PostgreSQL", "years": 2},
            {"position": "Python Developer", "company": "Freelance", "description": "Various web backend projects", "years": 1},
        ],
    },
    {   # Noah Anderson
        "full_name": "Noah Anderson",
        "phone": "+1-646-555-0177",
        "location": "New York, NY",
        "skills": ["AWS", "Kubernetes", "Terraform", "Docker", "Jenkins"],
        "education": [{"degree": "BSc", "institution": "NYU", "field_of_study": "Information Systems", "graduation_year": 2018}],
        "experience": [
            {"position": "DevOps Engineer", "company": "CloudOps Inc", "description": "AWS infrastructure and CI/CD pipelines", "years": 4},
            {"position": "SysAdmin", "company": "Media Corp", "description": "Linux server administration", "years": 2},
        ],
    },
    {   # Elena Popescu
        "full_name": "Elena Popescu",
        "phone": "+40-72-100-2000",
        "location": "Bucharest, Romania",
        "skills": ["Vue.js", "React", "CSS", "Figma", "TypeScript"],
        "education": [{"degree": "BSc", "institution": "University Politehnica Bucharest", "field_of_study": "Computer Science", "graduation_year": 2021}],
        "experience": [
            {"position": "Frontend Developer", "company": "Digital Agency RO", "description": "Vue.js and React SPA development", "years": 2},
            {"position": "UI Developer", "company": "Startup Bucharest", "description": "Component libraries and design systems", "years": 1},
        ],
    },
    {   # Kwame Asante
        "full_name": "Kwame Asante",
        "phone": "+233-55-100-2000",
        "location": "Accra, Ghana",
        "skills": ["Apache Spark", "Airflow", "Python", "SQL", "BigQuery"],
        "education": [{"degree": "BSc", "institution": "KNUST", "field_of_study": "Computer Engineering", "graduation_year": 2020}],
        "experience": [
            {"position": "Data Engineer", "company": "TelecomGhana", "description": "Built Spark pipelines for 50M+ records daily", "years": 3},
            {"position": "SQL Analyst", "company": "Bank of Ghana", "description": "Business intelligence and reporting", "years": 1},
        ],
    },
    {   # Sophie Martin
        "full_name": "Sophie Martin",
        "phone": "+33-6-12-00-00-01",
        "location": "Paris, France",
        "skills": ["Swift", "SwiftUI", "Xcode", "Combine", "CoreData"],
        "education": [{"degree": "MSc", "institution": "École Polytechnique", "field_of_study": "Computer Science", "graduation_year": 2019}],
        "experience": [
            {"position": "iOS Developer", "company": "MobileParis", "description": "Consumer-facing iOS app with 1M+ downloads", "years": 4},
            {"position": "Junior iOS Dev", "company": "Startup Lyon", "description": "Swift and Objective-C", "years": 1},
        ],
    },
    {   # Arjun Mehta
        "full_name": "Arjun Mehta",
        "phone": "+91-98765-00001",
        "location": "Bangalore, India",
        "skills": ["Penetration Testing", "Python", "Burp Suite", "OWASP", "Linux"],
        "education": [{"degree": "BTech", "institution": "IIT Bangalore", "field_of_study": "Computer Science", "graduation_year": 2017}],
        "experience": [
            {"position": "Security Engineer", "company": "CyberSec India", "description": "Red team assessments and bug bounty", "years": 5},
            {"position": "Security Analyst", "company": "Bank Secure", "description": "Vulnerability assessments and SAST", "years": 2},
        ],
    },
    {   # Isabelle Dumont
        "full_name": "Isabelle Dumont",
        "phone": "+33-6-12-00-00-02",
        "location": "Lyon, France",
        "skills": ["Product Strategy", "Agile", "Jira", "Data Analysis", "User Research"],
        "education": [{"degree": "MSc", "institution": "HEC Paris", "field_of_study": "Management", "graduation_year": 2019}],
        "experience": [
            {"position": "Product Manager", "company": "SaaS Lyon", "description": "Led product roadmap for B2B SaaS platform", "years": 4},
            {"position": "Business Analyst", "company": "Consulting Firm", "description": "Requirements gathering and process mapping", "years": 1},
        ],
    },
    {   # Omar Khalil
        "full_name": "Omar Khalil",
        "phone": "+971-50-999-0001",
        "location": "Dubai, UAE",
        "skills": ["Solidity", "Web3.js", "Hardhat", "Ethereum", "IPFS"],
        "education": [{"degree": "BSc", "institution": "AUS", "field_of_study": "Computer Science", "graduation_year": 2021}],
        "experience": [
            {"position": "Blockchain Developer", "company": "DeFi Dubai", "description": "Smart contracts and DeFi protocol dev", "years": 2},
            {"position": "Full-Stack Dev", "company": "Startup UAE", "description": "Web3 frontend with React", "years": 1},
        ],
    },
]

profile_ids = []
for i, cp in enumerate(candidate_profiles):
    res = cands_col.insert_one({
        **cp,
        "user_id": cand_ids[i],
        "cv_filename": None,
        "cv_path": None,
        "cv_text": None,
        "embedding_id": None,
        "created_at": now(random.randint(-55, -20)),
        "updated_at": now(random.randint(-19, -1)),
    })
    profile_ids.append(str(res.inserted_id))

print(f"   ✓ {len(profile_ids)} candidate profiles")

# ─── 4. Companies ─────────────────────────────────────────────────────────────
print("🏢 Creating companies...")
companies_data = [
    ("TechCorp Solutions",    "Leading provider of enterprise software solutions. We build tools that empower teams to work smarter and faster across the globe.",              "Software & IT",          "https://techcorp.io",  "San Francisco, CA", 500),
    ("Nova Inc.",             "Nova is a fast-growing fintech startup revolutionizing payment infrastructure for emerging markets worldwide.",                                   "Fintech",                "https://novainc.com",  "London, UK",        120),
    ("DataFlow Analytics",    "DataFlow helps enterprises unlock the value of their data with real-time analytics and AI-driven insights at scale.",                             "Data & Analytics",       "https://dataflow.io",  "Dubai, UAE",         80),
    ("SkyLab Technologies",   "SkyLab builds next-generation drone and autonomous systems for logistics, agriculture, and urban mobility.",                                       "Aerospace & Robotics",   "https://skylab.fr",    "Paris, France",      60),
    ("NexusAI",               "NexusAI develops cutting-edge AI models and APIs for natural language understanding, used by thousands of developers worldwide.",                  "Artificial Intelligence","https://nexusai.in",   "Bangalore, India",  200),
]

company_ids = []
for i, (name, desc, industry, website, location, size) in enumerate(companies_data):
    rid = rec_ids[i]
    res = companies_col.insert_one({
        "name": name, "description": desc, "industry": industry,
        "website": website, "location": location, "size": size,
        "created_by": rid,
        "created_at": now(random.randint(-85, -40)),
        "updated_at": now(random.randint(-39, -5)),
    })
    coid = str(res.inserted_id)
    company_ids.append(coid)
    members_col.insert_one({
        "company_id": coid, "recruiter_id": rid, "role": "owner",
        "created_at": now(-80),
    })

print(f"   ✓ {len(company_ids)} companies")

# ─── 5. Job Offers ────────────────────────────────────────────────────────────
print("📋 Creating job offers...")
jobs_data = [
    # TechCorp [0]
    {"title": "Senior Full-Stack Engineer",    "co": 0, "rec": 0, "skills": ["React","Node.js","TypeScript","PostgreSQL","Docker"],           "exp": 4, "loc": "San Francisco, CA (Hybrid)", "status": "open",
     "desc": "Join our core product team to build scalable web applications used by 1M+ users. You'll work across the entire stack with React and Node.js, mentor junior developers, and shape architectural decisions."},
    {"title": "DevOps Engineer",               "co": 0, "rec": 0, "skills": ["AWS","Kubernetes","Terraform","Docker","GitHub Actions"],         "exp": 3, "loc": "Remote",                        "status": "open",
     "desc": "Own our cloud infrastructure on AWS. Build and maintain CI/CD pipelines, improve reliability, and lead our move to Kubernetes. Work closely with engineering teams to ensure smooth deployments."},
    {"title": "Frontend Developer (React)",    "co": 0, "rec": 0, "skills": ["React","TypeScript","CSS","Figma","Jest"],                        "exp": 2, "loc": "San Francisco, CA",              "status": "open",
     "desc": "Build beautiful, performant user interfaces for our SaaS platform. Collaborate with designers and backend engineers to deliver pixel-perfect experiences with React and TypeScript."},
    # Nova [1]
    {"title": "Backend Engineer — Payments",   "co": 1, "rec": 1, "skills": ["Python","FastAPI","Kafka","PostgreSQL","Redis"],                  "exp": 3, "loc": "London, UK (Hybrid)",           "status": "open",
     "desc": "Build the payment processing engine powering millions of transactions. Work with Python microservices, Kafka, and PostgreSQL to ensure our system is reliable, secure, and blazing fast."},
    {"title": "iOS Developer",                 "co": 1, "rec": 1, "skills": ["Swift","SwiftUI","CoreData","Xcode","REST APIs"],                 "exp": 3, "loc": "London, UK",                    "status": "open",
     "desc": "Design and build native iOS features for our consumer-facing mobile app with 500k+ downloads. Ship high-quality Swift code and work with cross-functional squads in a fast-paced fintech environment."},
    {"title": "Security Engineer",             "co": 1, "rec": 1, "skills": ["Penetration Testing","Python","OWASP","Burp Suite","AWS Security"],"exp": 5, "loc": "London, UK",                    "status": "open",
     "desc": "Protect our financial infrastructure. Conduct security reviews and penetration tests, lead our bug bounty program, and partner with engineering to build security into every stage of the SDLC."},
    # DataFlow [2]
    {"title": "Data Engineer",                 "co": 2, "rec": 2, "skills": ["Apache Spark","Airflow","Python","SQL","BigQuery"],               "exp": 3, "loc": "Dubai, UAE",                    "status": "open",
     "desc": "Design and build data pipelines that process terabytes of data daily. Use Apache Spark and Airflow to deliver reliable, low-latency data products to our enterprise analytics customers."},
    {"title": "Machine Learning Engineer",     "co": 2, "rec": 2, "skills": ["Python","PyTorch","MLflow","Docker","SQL"],                       "exp": 4, "loc": "Dubai, UAE (Remote OK)",         "status": "open",
     "desc": "Build and deploy ML models powering our predictive analytics products. Own the full ML lifecycle from research to production using PyTorch and our internal ML platform."},
    # SkyLab [3]
    {"title": "Embedded Systems Engineer",     "co": 3, "rec": 3, "skills": ["C","C++","RTOS","Linux","CAN Bus"],                               "exp": 4, "loc": "Paris, France",                 "status": "open",
     "desc": "Develop firmware for autonomous drone systems. Work with real-time operating systems, sensor fusion algorithms, and communication protocols to push the limits of autonomous flight."},
    {"title": "Computer Vision Engineer",      "co": 3, "rec": 3, "skills": ["Python","OpenCV","PyTorch","SLAM","ROS"],                         "exp": 3, "loc": "Paris, France",                 "status": "open",
     "desc": "Build perception systems for autonomous drones using computer vision and deep learning. Work on object detection, SLAM, and obstacle avoidance in demanding real-world environments."},
    # NexusAI [4]
    {"title": "NLP Research Engineer",         "co": 4, "rec": 4, "skills": ["Python","PyTorch","Transformers","NLP","CUDA"],                   "exp": 4, "loc": "Bangalore, India",              "status": "open",
     "desc": "Research and productionize large language models for real-world applications. Push NLP state-of-the-art, fine-tune transformers, and ship APIs used by 50k+ developers every day."},
    {"title": "Product Manager — AI Platform", "co": 4, "rec": 4, "skills": ["Product Strategy","Agile","Data Analysis","AI/ML basics","Jira"],  "exp": 4, "loc": "Bangalore, India (Hybrid)",     "status": "open",
     "desc": "Define the vision and roadmap for our developer-facing AI API platform. Work with engineering, design, and go-to-market teams to ship features that delight developers building with AI."},
    {"title": "Blockchain Developer",          "co": 4, "rec": 4, "skills": ["Solidity","Web3.js","Hardhat","Ethereum","TypeScript"],            "exp": 2, "loc": "Remote",                        "status": "open",
     "desc": "Build smart contracts and decentralized protocols for our Web3 integrations. Work with Solidity, Hardhat, and Ethereum infrastructure in a team passionate about the future of open finance."},
    # Closed/Draft for realism
    {"title": "Platform Architect",            "co": 0, "rec": 0, "skills": ["System Design","AWS","Microservices","Go","PostgreSQL"],           "exp": 8, "loc": "San Francisco, CA",              "status": "closed",
     "desc": "Lead architectural decisions for our next-generation platform. This role has been successfully filled."},
    {"title": "Head of Data Science",          "co": 2, "rec": 2, "skills": ["Python","Machine Learning","Leadership","SQL","Statistics"],       "exp": 7, "loc": "Dubai, UAE",                    "status": "draft",
     "desc": "Lead a growing team of data scientists building predictive models. Currently in internal review — not yet published."},
]

job_ids = []
for jd in jobs_data:
    d = random.randint(5, 60)
    res = jobs_col.insert_one({
        "title": jd["title"],
        "company_id": company_ids[jd["co"]],
        "created_by": rec_ids[jd["rec"]],
        "description": jd["desc"],
        "required_skills": jd["skills"],
        "min_experience": jd["exp"],
        "location": jd["loc"],
        "status": jd["status"],
        "created_at": now(-d),
        "updated_at": now(-random.randint(1, d)),
    })
    job_ids.append(str(res.inserted_id))

open_count = sum(1 for jd in jobs_data if jd["status"] == "open")
print(f"   ✓ {len(job_ids)} job offers ({open_count} open, 1 closed, 1 draft)")

# ─── 6. Applications ──────────────────────────────────────────────────────────
print("📨 Creating applications...")

# (candidate_index, job_index, status, days_ago)
apps_plan = [
    (0, 0,  "pending",   -5),
    (0, 1,  "reviewing", -15),
    (1, 7,  "accepted",  -20),
    (1, 10, "pending",   -3),
    (2, 3,  "reviewing", -10),
    (2, 0,  "rejected",  -30),
    (3, 1,  "accepted",  -25),
    (3, 6,  "reviewing", -8),
    (4, 2,  "pending",   -2),
    (4, 11, "pending",   -4),
    (5, 6,  "reviewing", -12),
    (5, 7,  "pending",   -6),
    (6, 2,  "accepted",  -18),
    (6, 4,  "reviewing", -9),
    (7, 5,  "reviewing", -14),
    (7, 10, "pending",   -7),
    (8, 11, "accepted",  -22),
    (8, 9,  "reviewing", -11),
    (9, 12, "pending",   -3),
    (9, 3,  "reviewing", -16),
]

cover_letters = [
    "I'm very excited about this opportunity. With my background in {skill}, I'm confident I can make a real impact on your team from day one.",
    "After researching your company, I believe this role aligns perfectly with my experience and goals. I'd love to contribute to your mission.",
    "Your team's approach to engineering and product is exactly what I've been looking for. I bring {exp} years of hands-on experience with {skill}.",
    None,
    "I've been following your company's work closely and am impressed by the technical challenges you're solving. I'd be thrilled to join.",
    "This position matches my skills and career direction perfectly. I'm passionate about {skill} and would love to bring that energy to your team.",
    None,
    "I believe great products come from great teams. I'd love the opportunity to collaborate with your engineers on challenging problems.",
]

cand_skills = [
    ["React", "Node.js"], ["PyTorch", "NLP"], ["FastAPI", "PostgreSQL"],
    ["Kubernetes", "AWS"], ["Vue.js", "CSS"], ["Spark", "Airflow"],
    ["Swift", "SwiftUI"], ["Penetration Testing"], ["Product Strategy", "Agile"],
    ["Solidity", "Web3.js"],
]
cand_exps = [4, 5, 3, 6, 3, 4, 5, 7, 5, 3]

n = 0
seen = set()
for ci, ji, st, days in apps_plan:
    if (ci, ji) in seen: continue
    seen.add((ci, ji))
    cl = random.choice(cover_letters)
    if cl:
        skill = cand_skills[ci][0] if cand_skills[ci] else "technology"
        cl = cl.replace("{skill}", skill).replace("{exp}", str(cand_exps[ci]))
    t = now(days)
    apps_col.insert_one({
        "candidate_id": profile_ids[ci],
        "job_offer_id": job_ids[ji],
        "cover_letter": cl,
        "status": st,
        "applied_at": t,
        "updated_at": t + timedelta(days=random.randint(1, 3)),
    })
    n += 1

print(f"   ✓ {n} applications")

# ─── Summary ──────────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("✅  Seed complete!")
print("=" * 60)
print()
print("🔑  Login credentials:")
print()
print("  ADMIN")
print("    admin@smartrecruit.io  /  Admin@1234")
print()
print("  RECRUITERS  (password: Recruiter@1234)")
for email, name, *_ in recruiter_specs:
    print(f"    {name:<20}  {email}")
print()
print("  CANDIDATES  (password: Candidate@1234)")
for email, name in candidate_specs:
    print(f"    {name:<20}  {email}")
print()
print(f"  Companies  : {len(company_ids)}")
print(f"  Job Offers : {len(job_ids)} ({open_count} open)")
print(f"  Applications: {n}")
