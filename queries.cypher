// 1. Multi-hop: candidate -> skill -> job -> company -> domain
MATCH (c:Candidate {id: $candidateId})-[:HAS_SKILL]->(s:Skill)
      <-[:REQUIRES_SKILL]-(j:Job)-[:AT_COMPANY]->(co:Company)
      -[:IN_DOMAIN]->(d:Domain)
RETURN c.name, j.title, co.name, d.name, collect(DISTINCT s.name) AS matchedSkills
ORDER BY size(matchedSkills) DESC;

// 2. Find skill gaps for a candidate and a job
MATCH (c:Candidate {id: $candidateId})
MATCH (j:Job {id: $jobId})-[:REQUIRES_SKILL]->(s:Skill)
WHERE NOT (c)-[:HAS_SKILL]->(s)
RETURN j.title, collect(s.name) AS missingSkills;

// 3. Find jobs sharing skills with a candidate
MATCH (c:Candidate {id: $candidateId})-[:HAS_SKILL]->(s:Skill)
      <-[:REQUIRES_SKILL]-(j:Job)
RETURN j.title, collect(DISTINCT s.name) AS sharedSkills
ORDER BY size(sharedSkills) DESC;

// 4. Graph query that is awkward in a simple relational schema:
// find candidates who are connected to jobs in a domain through shared skills.
MATCH (c:Candidate)-[:HAS_SKILL]->(s:Skill)
      <-[:REQUIRES_SKILL]-(j:Job)-[:IN_DOMAIN]->(d:Domain)
WHERE d.name = $domain
RETURN c.name, collect(DISTINCT s.name) AS relevantSkills, count(DISTINCT j) AS reachableJobs
ORDER BY reachableJobs DESC;
