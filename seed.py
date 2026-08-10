import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("COGNODB_URI")
USER = os.getenv("COGNODB_USER", "cognodb")
PASSWORD = os.getenv("COGNODB_PASSWORD")

if not URI or not PASSWORD:
    raise RuntimeError("Set COGNODB_URI and COGNODB_PASSWORD in .env")

driver = GraphDatabase.driver(
    URI,
    auth=(USER, PASSWORD)
)

CONSTRAINTS = [
    "CREATE CONSTRAINT candidate_id IF NOT EXISTS FOR (n:Candidate) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT skill_name IF NOT EXISTS FOR (n:Skill) REQUIRE n.name IS UNIQUE",
    "CREATE CONSTRAINT job_id IF NOT EXISTS FOR (n:Job) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT company_name IF NOT EXISTS FOR (n:Company) REQUIRE n.name IS UNIQUE",
    "CREATE CONSTRAINT domain_name IF NOT EXISTS FOR (n:Domain) REQUIRE n.name IS UNIQUE",
]

CANDIDATE_QUERY = """
UNWIND $candidates AS row
MERGE (c:Candidate {id: row.id})
SET c.name = row.name,
    c.title = row.title
WITH row, c
UNWIND row.skills AS skillName
MERGE (s:Skill {name: skillName})
MERGE (c)-[:HAS_SKILL]->(s)
"""

JOB_QUERY = """
UNWIND $jobs AS row
MERGE (j:Job {id: row.id})
SET j.title = row.title,
    j.location = row.location,
    j.description = row.description

MERGE (co:Company {name: row.company})
MERGE (d:Domain {name: row.domain})

MERGE (j)-[:AT_COMPANY]->(co)
MERGE (j)-[:IN_DOMAIN]->(d)

WITH row, j
UNWIND row.skills AS skillName
MERGE (s:Skill {name: skillName})
MERGE (j)-[:REQUIRES_SKILL]->(s)
"""

CANDIDATES = [
    {
        "id": "c1",
        "name": "Asha Rao",
        "title": "Junior Software Engineer",
        "skills": ["Python", "SQL", "JavaScript", "Git"]
    },
    {
        "id": "c2",
        "name": "Rahul Mehta",
        "title": "Data Analyst",
        "skills": ["Python", "SQL", "Power BI", "Excel"]
    },
    {
        "id": "c3",
        "name": "Neha Singh",
        "title": "Frontend Developer",
        "skills": ["JavaScript", "React", "HTML", "CSS", "Git"]
    }
]

JOBS = [
    {
        "id": "j1",
        "title": "Backend Python Developer",
        "company": "NovaTech",
        "domain": "SaaS",
        "location": "Hyderabad",
        "description": "Build APIs and backend services.",
        "skills": ["Python", "SQL", "Git"]
    },
    {
        "id": "j2",
        "title": "Data Analyst",
        "company": "InsightWorks",
        "domain": "Analytics",
        "location": "Hyderabad",
        "description": "Analyze business data and create dashboards.",
        "skills": ["Python", "SQL", "Power BI", "Excel"]
    },
    {
        "id": "j3",
        "title": "Frontend React Developer",
        "company": "PixelForge",
        "domain": "SaaS",
        "location": "Remote",
        "description": "Build accessible React interfaces.",
        "skills": ["JavaScript", "React", "HTML", "CSS", "Git"]
    },
    {
        "id": "j4",
        "title": "Full Stack Engineer",
        "company": "CloudNest",
        "domain": "FinTech",
        "location": "Bengaluru",
        "description": "Work across APIs and web applications.",
        "skills": ["JavaScript", "React", "Python", "SQL", "Git"]
    },
    {
        "id": "j5",
        "title": "BI Developer",
        "company": "InsightWorks",
        "domain": "Analytics",
        "location": "Remote",
        "description": "Create reporting models and dashboards.",
        "skills": ["SQL", "Power BI", "Excel"]
    }
]


def main():
    try:
        driver.verify_connectivity()
        print("CognoDB connection successful.")

        with driver.session() as session:

            for query in CONSTRAINTS:
                session.run(query)

            session.run(
                CANDIDATE_QUERY,
                candidates=CANDIDATES
            )

            session.run(
                JOB_QUERY,
                jobs=JOBS
            )

        print("CognoDB seed completed successfully.")

    except Exception as e:
        print("Seed failed:")
        print(e)

    finally:
        driver.close()


if __name__ == "__main__":
    main()