# Sasafix Backend Setup Guide

## 1. Clone the Repository
```bash
git clone <repo_url>
cd sasa-fix-backend
```
---
# 2. Create a Virtual Environment

```bash
python3 -m venv venv
```
Activate the environment:

```bash
source venv/bin/activate
```
---
# 3. Install Dependencies
```bash
pip install -r requirements.txt
```
---
# 4. Setup PostgreSQL
Check if PostgreSQL is installed:
```bash
psql --version
```
Start the PostgreSQL service:

```bash
sudo service postgresql start
```
---
# 5. Create the Database and User
Open PostgreSQL:
```bash
sudo -u postgres psql
```
Run the following commands:
```sql
CREATE DATABASE sasafix_db;

CREATE USER yourname WITH PASSWORD 'strongpassword';

ALTER ROLE yourname/username SET client_encoding TO 'utf8';
ALTER ROLE yourname/username SET default_transaction_isolation TO 'read committed';
ALTER ROLE yourname/username SET timezone TO 'UTC';

GRANT ALL PRIVILEGES ON DATABASE sasafix_db TO yourname/username;
```
Exit PostgreSQL:
```sql
\q
```
---
# 6. Configure Environment Variables
Create a `.env` file in the project root:
```
DATABASE_URL=postgresql://yourusername:strongpassword@localhost:5432/sasafix
```
---
# 7. Run Database Migrations
```bash
alembic upgrade head
```
---
# 8. Run the Development Server
```bash
uvicorn server.main:app --reload
```
The API will be available at:
```
http://127.0.0.1:8000
```
---
# 9. Create Your Own Development Branch
Each developer should create a branch using your name.
Example:
```bash
git checkout -b name
```
Push your branch:

```bash
git push origin name
```
Always work on **your branch**, not `main`.
---
# 10. API Documentation
FastAPI automatically generates documentation.
Swagger UI:
```
http://127.0.0.1:8000/docs
```
ReDoc:

```
http://127.0.0.1:8000/redoc
```
