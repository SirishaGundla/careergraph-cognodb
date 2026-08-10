import os

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from neo4j import GraphDatabase


# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# CognoDB connection details
URI = os.getenv("COGNODB_URI")
USER = os.getenv("COGNODB_USER", "cognodb")
PASSWORD = os.getenv("COGNODB_PASSWORD")


if not URI or not PASSWORD:
    raise RuntimeError(
        "Set COGNODB_URI and COGNODB_PASSWORD in your .env file."
    )


# Create CognoDB driver
driver = GraphDatabase.driver(
    URI,
    auth=(USER, PASSWORD)
)


def run_query(query, params=None):
    """Run a Cypher query and return records as dictionaries."""
    with driver.session() as session:
        result = session.run(query, params or {})
        return [record.data() for record in result]


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------

@app.get("/")
def home():
    return render_template("index.html")


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@app.get("/api/health")
def health():
    try:
        run_query("RETURN 1 AS ok")
        return jsonify({
            "ok": True
        })

    except Exception as exc:
        return jsonify({
            "ok": False,
            "error": str(exc)
        }), 503


# ---------------------------------------------------------
# CANDIDATES
# ---------------------------------------------------------

@app.get("/api/candidates")
def candidates():

    query = """
    MATCH (c:Candidate)
    RETURN
        c.id AS id,
        c.name AS name,
        c.title AS title
    ORDER BY c.name
    """

    try:
        return jsonify(run_query(query))

    except Exception as exc:
        return jsonify({
            "error": str(exc)
        }), 503


# ---------------------------------------------------------
# JOBS
# ---------------------------------------------------------

@app.get("/api/jobs")
def jobs():

    q = request.args.get("q", "").strip()

    query = """
    MATCH (j:Job)-[:AT_COMPANY]->(co:Company)

    OPTIONAL MATCH (j)-[:IN_DOMAIN]->(d:Domain)

    WHERE $q = ""
       OR toLower(j.title) CONTAINS toLower($q)
       OR toLower(co.name) CONTAINS toLower($q)
       OR toLower(d.name) CONTAINS toLower($q)

    RETURN
        j.id AS id,
        j.title AS title,
        j.location AS location,
        j.description AS description,
        co.name AS company,
        d.name AS domain

    ORDER BY j.title

    LIMIT 50
    """

    try:
        return jsonify(
            run_query(query, {"q": q})
        )

    except Exception as exc:
        return jsonify({
            "error": str(exc)
        }), 503


# ---------------------------------------------------------
# JOB RECOMMENDATIONS
# Candidate -> Skill <- Job -> Company -> Domain
# ---------------------------------------------------------

@app.get("/api/recommendations/<candidate_id>")
def recommendations(candidate_id):

    query = """
    MATCH (c:Candidate {id: $candidate_id})
          -[:HAS_SKILL]->(s:Skill)
          <-[:REQUIRES_SKILL]-(j:Job)
          -[:AT_COMPANY]->(co:Company)
          -[:IN_DOMAIN]->(d:Domain)

    WITH
        c,
        j,
        co,
        d,
        collect(DISTINCT s.name) AS matchedSkills

    OPTIONAL MATCH (j)-[:REQUIRES_SKILL]->(requiredSkill:Skill)

    WITH
        j,
        co,
        d,
        matchedSkills,
        collect(DISTINCT requiredSkill.name) AS requiredSkills

    WITH
        j,
        co,
        d,
        matchedSkills,
        requiredSkills,
        size(matchedSkills) AS matchCount

    RETURN
        j.id AS id,
        j.title AS title,
        co.name AS company,
        d.name AS domain,
        j.location AS location,
        matchedSkills,
        requiredSkills,
        matchCount,
        CASE
            WHEN size(requiredSkills) = 0
            THEN 0
            ELSE toInteger(
                100.0 * matchCount / size(requiredSkills)
            )
        END AS matchPercent

    ORDER BY
        matchPercent DESC,
        matchCount DESC,
        j.title

    LIMIT 20
    """

    try:
        return jsonify(
            run_query(
                query,
                {"candidate_id": candidate_id}
            )
        )

    except Exception as exc:
        return jsonify({
            "error": str(exc)
        }), 503


# ---------------------------------------------------------
# SKILL GAPS
# Candidate -> Job -> Required Skills
# ---------------------------------------------------------

@app.get("/api/skill-gaps/<candidate_id>/<job_id>")
def skill_gaps(candidate_id, job_id):

    query = """
    MATCH (c:Candidate {id: $candidate_id})

    MATCH (j:Job {id: $job_id})
          -[:REQUIRES_SKILL]->(requiredSkill:Skill)

    WHERE NOT (c)-[:HAS_SKILL]->(requiredSkill)

    RETURN
        j.title AS job,
        collect(requiredSkill.name) AS missingSkills
    """

    try:

        rows = run_query(
            query,
            {
                "candidate_id": candidate_id,
                "job_id": job_id
            }
        )

        if rows:
            return jsonify(rows[0])

        return jsonify({
            "job": None,
            "missingSkills": []
        })

    except Exception as exc:
        return jsonify({
            "error": str(exc)
        }), 503


# ---------------------------------------------------------
# DATABASE STATISTICS
# ---------------------------------------------------------

@app.get("/api/stats")
def stats():

    query = """
    OPTIONAL MATCH (c:Candidate)
    WITH count(c) AS candidates

    OPTIONAL MATCH (j:Job)
    WITH candidates, count(j) AS jobs

    OPTIONAL MATCH (s:Skill)
    WITH candidates, jobs, count(s) AS skills

    OPTIONAL MATCH (co:Company)
    WITH candidates, jobs, skills, count(co) AS companies

    RETURN
        candidates,
        jobs,
        skills,
        companies
    """

    try:

        rows = run_query(query)

        if rows:
            return jsonify(rows[0])

        return jsonify({
            "candidates": 0,
            "jobs": 0,
            "skills": 0,
            "companies": 0
        })

    except Exception as exc:
        return jsonify({
            "error": str(exc)
        }), 503


# ---------------------------------------------------------
# APPLICATION SHUTDOWN
# ---------------------------------------------------------

@app.teardown_appcontext
def close_driver(exception=None):
    # Driver remains alive for the entire application lifetime.
    pass


# ---------------------------------------------------------
# START FLASK SERVER
# ---------------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=False
    )