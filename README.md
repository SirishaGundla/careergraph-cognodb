<<<<<<< HEAD
# CareerGraph

A graph-powered career discovery application built with Flask, Python and CognoDB.

## Features

- Candidate skill matching
- Job recommendations
- Skill gap analysis
- Job/company/domain exploration
- Multi-hop graph traversal
- Search functionality

## Why a Graph Database?

Career relationships naturally form a graph:

Candidate → Skill → Job → Company → Domain

A graph database makes it easier to traverse these relationships and discover connections between candidates, skills, jobs and companies.

## Data Model

Candidate
↓ HAS_SKILL
Skill
↑ REQUIRES_SKILL
Job
↓ AT_COMPANY
Company
↓ IN_DOMAIN
Domain

## Technology Stack

- Python
- Flask
- CognoDB
- Neo4j Python Driver
- Cypher
- HTML
- CSS
- JavaScript

## Setup

### 1. Clone repository

git clone YOUR_GITHUB_URL

### 2. Create virtual environment

python -m venv .venv

### 3. Activate environment

.venv\Scripts\activate

### 4. Install dependencies

pip install -r requirements.txt

### 5. Configure environment variables

Create `.env`:

COGNODB_URI=your_uri
COGNODB_USER=cognodb
COGNODB_PASSWORD=your_password
PORT=5000

### 6. Seed database

python seed.py

### 7. Run application

python app.py

Open:

http://127.0.0.1:5000

## Main Graph Queries

### Multi-hop recommendation

Candidate → Skill → Job → Company → Domain

### Skill gap analysis

Find skills required by a job that the candidate does not have.

### Shared skills

Find jobs that share skills with a candidate.

### Domain traversal

Find candidates connected to jobs in a particular domain.

## Screenshots
![alt text](<Screenshot (89).png>)
![alt text](<Screenshot (85).png>)
![alt text](<Screenshot (86).png>)
![alt text](<Screenshot (87).png>)
![alt text](<Screenshot (88).png>)
![alt text](<Screenshot (90).png>)
=======
# careergraph-cognodb
>>>>>>> 24ccc41af5eb0d34e43c2220d750323ffa9ee17d
