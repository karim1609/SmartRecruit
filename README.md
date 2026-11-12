# SmartRecruit — AI-Powered Recruitment Platform

## 1. Project Overview

**SmartRecruit** is an AI-powered recruitment platform designed to simplify and improve the recruitment process by connecting recruiters with the most relevant candidates for their job offers.

The platform allows candidates to create professional profiles, upload their CVs, explore job opportunities, and submit applications.

Recruiters can manage companies, publish job offers, review applications, and eventually use AI-powered matching to identify the most relevant candidates.

Administrators manage the platform, users, companies, job offers, and overall activity.

The main objective is to build a recruitment platform that combines traditional recruitment management with semantic search and artificial intelligence.

---

## 2. Main Objectives

- Provide secure authentication and role-based access control.
- Allow candidates to manage their professional profiles.
- Allow recruiters to manage companies and job offers.
- Allow candidates to apply for job offers.
- Allow recruiters to manage received applications.
- Provide administrators with platform-wide management tools.
- Provide role-specific dashboards and statistics.
- Integrate AI-based candidate/job matching using semantic embeddings.
- Return the top 5 most relevant candidates for a job offer.
- Provide a modern, responsive, and user-friendly interface.

---

## 3. Technology Stack

### Backend

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| FastAPI | REST API framework |
| Pydantic | Data validation and schemas |
| PyMongo | MongoDB integration |
| MongoDB | Main database |
| JWT | Authentication |
| Argon2 | Password hashing |
| PyMuPDF | PDF CV text extraction |
| Sentence Transformers | Text embeddings |
| Qdrant | Vector database |
| Redis | Caching |
| Neo4j | Graph database integration |
| Docker | Containerization |

### Frontend

The frontend must be developed using:

| Technology | Purpose |
|---|---|
| React | UI development |
| Vite | Frontend build tool |
| JavaScript | Main frontend language |
| Tailwind CSS | Styling |
| Axios | HTTP requests |
| React Router DOM | Navigation |
| Lucide React | Icons |
| Recharts | Dashboard charts |
| React Hot Toast | Notifications |

Use reusable React components and a modular architecture.

### Infrastructure

- Docker and Docker Compose.
- Backend and frontend run as separate services.
- MongoDB is the primary database.
- Qdrant, Redis, and Neo4j are intended for additional services.

---

## 4. System Architecture

```text
                    SMARTRECRUIT
                         |
              +----------+----------+
              |                     |
          FRONTEND                BACKEND
         React + Vite              FastAPI
              |                     |
              |                REST API Routes
              |                     |
              |          +----------+----------+
              |          |          |          |
              |        Auth       Users     Candidates
              |          |          |          |
              |       Recruiters  Companies  Job Offers
              |          |          |          |
              |      Applications Dashboard Matching
              |                     |
              |                 SERVICES
              |                     |
              |          +----------+----------+
              |          |          |          |
              |        MongoDB    Qdrant     Redis
              |          |
              |        Neo4j
              |
              +-------- HTTP / JSON --------+
```

The frontend communicates with FastAPI through HTTP requests using Axios.

All protected requests must include the JWT access token in the Authorization header.

---

## 5. User Roles and Permissions

SmartRecruit supports three roles.

### 5.1 Candidate

Candidates can:

- Register and log in.
- View and update their personal profile.
- Manage their professional information.
- Add skills, education, and experience.
- Browse available job offers.
- View job offer details.
- Submit applications.
- View their own applications.
- Update the cover letter of a pending application.
- Withdraw an application.
- View application statistics on their dashboard.

Candidate navigation:

```text
Dashboard
My Profile
Browse Jobs
My Applications
Settings
Logout
```

### 5.2 Recruiter

Recruiters can:

- Register and log in.
- Manage their recruiter profile.
- Create and manage companies.
- View companies where they are members.
- Create job offers for authorized companies.
- View their job offers.
- Update and delete authorized job offers.
- View applications received for their authorized jobs.
- Review applications.
- Update application statuses.
- Access candidate matching functionality when the AI service is available.
- View recruiter statistics.

Recruiter navigation:

```text
Dashboard
My Profile
Companies
Job Offers
Applications
AI Matching
Settings
Logout
```

### 5.3 Administrator

Administrators have platform-wide management permissions.

They can:

- View platform statistics.
- List all registered users.
- View individual user details.
- Activate or deactivate user accounts.
- List all companies.
- Delete companies and related job offers.
- List all job offers.
- Delete job offers and related applications.
- View all applications.
- Access administrative dashboards.

Administrator navigation:

```text
Dashboard
Users
Candidates
Recruiters
Companies
Job Offers
Applications
Settings
Logout
```

Important: The frontend must never determine permissions independently. Backend authorization is authoritative.

---

## 6. Backend API Structure

The backend API uses the following routes.

Base URL during local development:

```text
http://localhost:8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

### 6.1 Authentication — `/auth`

| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | `/auth/register` | Register a new account | Public |
| POST | `/auth/login` | Authenticate and receive JWT | Public |
| GET | `/auth/me` | Get authenticated user information | Authenticated |

Registration supports two public roles:

- `candidate`
- `recruiter`

An administrator account must be created through a protected administrative process, not public registration.

Login accepts JSON credentials according to the existing backend implementation.

Example:

```json
{
  "email": "candidate@example.com",
  "password": "password123"
}
```

Expected login response structure:

```json
{
  "access_token": "JWT_TOKEN",
  "token_type": "bearer",
  "user": {
    "id": "USER_ID",
    "email": "candidate@example.com",
    "role": "candidate"
  }
}
```

### 6.2 Users — `/users`

| Method | Endpoint | Description | Access |
|---|---|---|---|
| GET | `/users/` | List users with pagination | Admin |
| GET | `/users/{user_id}` | Get user details | Admin |
| PATCH | `/users/{user_id}/status` | Activate/deactivate user | Admin |

Pagination example:

```text
GET /users/?skip=0&limit=20
```

Update user status:

```json
{
  "is_active": false
}
```

### 6.3 Candidates — `/candidates`

| Method | Endpoint | Description | Access |
|---|---|---|---|
| GET | `/candidates/me` | Get current candidate profile | Candidate |
| PATCH | `/candidates/me` | Update candidate profile | Candidate |

Candidate profile information:

- Full name
- Phone
- Location
- Skills
- Education
- Experience
- CV information where supported

Example profile:

```json
{
  "full_name": "John Doe",
  "phone": "+212600000000",
  "location": "Morocco",
  "skills": [
    "Python",
    "FastAPI",
    "MongoDB",
    "React"
  ],
  "education": [],
  "experience": []
}
```

Do not expose internal CV storage paths or extracted private CV text in public profile responses.

### 6.4 Recruiters — `/recruiters`

| Method | Endpoint | Description | Access |
|---|---|---|---|
| GET | `/recruiters/me` | Get current recruiter profile | Recruiter |
| PATCH | `/recruiters/me` | Update recruiter profile | Recruiter |

Recruiter information:

- Full name
- Phone
- Job title
- Company membership information

### 6.5 Companies — `/companies`

| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | `/companies/` | Create company | Recruiter |
| GET | `/companies/me` | List recruiter companies | Recruiter |
| GET | `/companies/{company_id}` | Get company details | Member/Admin |
| PATCH | `/companies/{company_id}` | Update company | Owner/Admin |

Company information:

- Name
- Description
- Industry
- Website
- Location
- Size
- Creation date
- Update date

A recruiter creating a company becomes its owner.

Company memberships are managed separately from recruiter profiles.

### 6.6 Job Offers — `/job-offers`

| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | `/job-offers/` | Create job offer | Recruiter |
| GET | `/job-offers/` | List public open job offers | Public |
| GET | `/job-offers/my` | List recruiter job offers | Recruiter |
| GET | `/job-offers/{job_offer_id}` | Get job offer details | Public, if open |
| PATCH | `/job-offers/{job_offer_id}` | Update job offer | Authorized Recruiter/Admin |
| DELETE | `/job-offers/{job_offer_id}` | Delete job offer | Authorized Recruiter/Admin |

Job offer information:

- Title
- Company ID
- Description
- Required skills
- Minimum experience
- Location
- Status
- Creation date
- Update date

Possible statuses:

```text
open
closed
draft
```

Example:

```json
{
  "title": "Python Developer",
  "company_id": "COMPANY_ID",
  "description": "We are looking for a Python developer.",
  "required_skills": [
    "Python",
    "FastAPI",
    "MongoDB"
  ],
  "min_experience": 1,
  "location": "Casablanca",
  "status": "open"
}
```

### 6.7 Applications — `/applications`

| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | `/applications/` | Apply for job offer | Candidate |
| GET | `/applications/my` | Get candidate applications | Candidate |
| GET | `/applications/received` | Get received applications | Recruiter/Admin |
| GET | `/applications/{application_id}` | Get application details | Authorized User |
| PATCH | `/applications/{application_id}` | Update application | Authorized User |
| DELETE | `/applications/{application_id}` | Withdraw application | Candidate |

Application statuses:

```text
pending
reviewing
accepted
rejected
```

Example application request:

```json
{
  "job_offer_id": "JOB_ID",
  "cover_letter": "I am interested in this position."
}
```

The backend automatically identifies the candidate from the authenticated user.

Recruiters can update application statuses only for applications they are authorized to manage.

### 6.8 Dashboard — `/dashboard`

| Method | Endpoint | Description | Access |
|---|---|---|---|
| GET | `/dashboard/` | Get role-specific dashboard information | Authenticated |

The backend detects the user's role and returns different statistics.

Candidate dashboard:

- Total applications
- Pending applications
- Applications under review
- Accepted applications
- Rejected applications
- Recent applications

Recruiter dashboard:

- Total job offers
- Open job offers
- Closed job offers
- Total applications received
- Pending applications
- Accepted applications
- Recent job offers

Admin dashboard:

- Total users
- Active users
- Total candidates
- Total recruiters
- Total companies
- Total job offers
- Open job offers
- Total applications
- Application statistics
- Recently registered users

The frontend should use the returned data to generate statistics cards, charts, and recent activity tables.

### 6.9 AI Matching — `/matching`

| Method | Endpoint | Description | Access |
|---|---|---|---|
| GET | `/matching/job/{job_id}` | Find matching candidates | Recruiter/Admin |
| GET | `/matching/health` | Initial matching route status | Recruiter/Admin |

Matching endpoint example:

```text
GET /matching/job/JOB_ID?top_k=5
```

The intended matching result contains:

- Candidate ID
- Candidate name
- Semantic similarity score
- Matched skills

The matching service must eventually use Sentence Transformers and Qdrant.

**Important:** AI matching is not yet fully implemented. The frontend must handle unavailable matching services gracefully and must not display fabricated candidate scores.

A similarity score represents semantic similarity, not the probability of hiring.

---

## 7. Frontend Architecture

Use a modular architecture.

Recommended structure:

```text
frontend/
│
├── public/
│
├── src/
│   │
│   ├── api/
│   │   ├── axios.js
│   │   ├── auth.js
│   │   ├── users.js
│   │   ├── candidates.js
│   │   ├── recruiters.js
│   │   ├── companies.js
│   │   ├── jobOffers.js
│   │   ├── applications.js
│   │   ├── dashboard.js
│   │   └── matching.js
│   │
│   ├── components/
│   │   ├── common/
│   │   ├── ui/
│   │   ├── Sidebar.jsx
│   │   ├── Navbar.jsx
│   │   ├── StatCard.jsx
│   │   ├── DataTable.jsx
│   │   ├── Modal.jsx
│   │   ├── Loading.jsx
│   │   └── ErrorMessage.jsx
│   │
│   ├── context/
│   │   └── AuthContext.jsx
│   │
│   ├── layouts/
│   │   ├── AuthLayout.jsx
│   │   └── DashboardLayout.jsx
│   │
│   ├── pages/
│   │   ├── auth/
│   │   │   ├── Login.jsx
│   │   │   └── Register.jsx
│   │   │
│   │   ├── admin/
│   │   │   ├── AdminDashboard.jsx
│   │   │   ├── Users.jsx
│   │   │   ├── Companies.jsx
│   │   │   ├── JobOffers.jsx
│   │   │   └── Applications.jsx
│   │   │
│   │   ├── candidate/
│   │   │   ├── CandidateDashboard.jsx
│   │   │   ├── CandidateProfile.jsx
│   │   │   ├── BrowseJobs.jsx
│   │   │   └── MyApplications.jsx
│   │   │
│   │   ├── recruiter/
│   │   │   ├── RecruiterDashboard.jsx
│   │   │   ├── RecruiterProfile.jsx
│   │   │   ├── Companies.jsx
│   │   │   ├── JobOffers.jsx
│   │   │   ├── Applications.jsx
│   │   │   └── Matching.jsx
│   │   │
│   │   └── NotFound.jsx
│   │
│   ├── routes/
│   │   └── ProtectedRoute.jsx
│   │
│   ├── hooks/
│   │
│   ├── utils/
│   │
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
│
├── .env
├── .env.example
├── package.json
└── vite.config.js
```

This structure is a recommendation. It can be adjusted if needed, but keep API logic separate from page components.

---

## 8. API Integration Requirements

### Axios configuration

Create a central Axios instance.

Base URL:

```env
VITE_API_URL=http://localhost:8000
```

Axios should:

1. Use `VITE_API_URL` as its base URL.
2. Add the JWT token to protected requests.
3. Set JSON content type when sending JSON.
4. Handle HTTP errors consistently.
5. Handle expired or invalid tokens.
6. Avoid repeating API configuration in individual pages.

Authorization header:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Authentication flow

1. User submits login form.
2. Frontend calls `POST /auth/login`.
3. Backend returns an access token and user information.
4. Frontend stores the token using an appropriate secure approach.
5. Frontend retrieves the current user through `GET /auth/me` when necessary.
6. Frontend redirects the user according to their role.
7. Protected routes prevent unauthorized navigation.
8. Logout clears the local authentication state.

For a production deployment, prefer secure HttpOnly cookies where the backend supports them. If using bearer tokens in browser storage during development, understand the XSS risks and avoid treating localStorage as a production security solution.

### Role-based navigation

Implement a shared dashboard layout.

The sidebar must change based on the authenticated user's role.

Do not create three completely separate UI systems. Reuse common components and layouts.

---

## 9. UI/UX Design Requirements

The interface should look like a modern professional SaaS recruitment platform.

Design direction:

- Clean and minimal.
- Professional enterprise SaaS appearance.
- Consistent spacing and typography.
- Modern dashboard cards.
- Clear tables and filters.
- Responsive sidebar.
- Smooth but subtle transitions.
- Consistent icons.
- Good visual hierarchy.
- Light theme as the primary theme.
- Optional dark mode if it does not delay core functionality.

Suggested visual direction:

- Primary color: deep navy or indigo.
- Background: light neutral gray.
- Cards: white with subtle borders.
- Text: dark slate.
- Accent color: blue or violet.
- Success: green.
- Warning: amber.
- Error: red.

Avoid excessive gradients, oversized cards, unnecessary animations, and decorative elements that reduce usability.

### Dashboard design

Each dashboard should contain:

- Page title and short description.
- Statistics cards.
- Relevant charts where useful.
- Recent activity.
- Quick actions.
- Loading, empty, and error states.

### Tables

Tables should support:

- Pagination where appropriate.
- Search.
- Status badges.
- Sorting where useful.
- Action menus.
- Confirmation dialogs for destructive actions.

### Forms

Forms must include:

- Required-field validation.
- Clear labels.
- Error messages.
- Loading state during submission.
- Success notifications.
- Cancel and submit actions.

Use modal dialogs for simple creation and editing operations where appropriate.

---

## 10. Important Development Constraints

1. Do not invent backend endpoints.
2. Use only the endpoints documented in this README or verified in the FastAPI OpenAPI documentation.
3. Do not fabricate API responses.
4. Do not generate fake AI matching scores.
5. Do not expose password hashes or private CV storage paths.
6. Do not let users change their own roles.
7. Do not allow candidates to access recruiter or admin pages.
8. Do not allow recruiters to access administrative operations.
9. Backend authorization is authoritative, even if frontend routes are protected.
10. Use the actual response fields returned by the backend.
11. Keep API requests in the `src/api/` directory.
12. Use reusable components instead of duplicating code.
13. Handle errors and loading states throughout the application.
14. Ensure the frontend works with real backend data.
15. Avoid implementing unnecessary mock data once backend integration is available.

If an API response differs from an example in this README, inspect the actual backend implementation and `/docs`. Do not silently change backend contracts just to fit an assumed frontend response.

---

## 11. Current Backend Development Status

The following route files have been implemented:

```text
backend/app/routes/
│
├── __init__.py
├── auth.py
├── users.py
├── candidates.py
├── recruiters.py
├── companies.py
├── job_offers.py
├── applications.py
├── admin.py
├── dashboard.py
└── matching.py
```

The current priority is to build and validate the frontend against these routes.

The following AI functionality is planned but requires additional service implementation and integration:

- CV PDF extraction.
- Text preprocessing.
- Sentence Transformer embedding generation.
- Qdrant vector storage.
- Semantic similarity search.
- Candidate ranking.
- Skill matching.
- AI matching result generation.

The matching route currently depends on a service function that must be implemented:

```python
find_top_candidates_for_job(job, top_k)
```

Do not assume this function or the complete AI pipeline is already operational.

---

## 12. Development and Execution

### Backend

From the backend directory:

```powershell
cd backend
```

Activate the virtual environment if one is configured:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Start FastAPI:

```powershell
uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

### Frontend

From the project root:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Start development server:

```powershell
npm run dev
```

Frontend:

```text
http://localhost:5173
```

### Environment variables

Frontend `.env`:

```env
VITE_API_URL=http://localhost:8000
```

Backend environment variables should be configured separately, including:

```env
MONGODB_URI=
MONGODB_DATABASE=
JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Use the actual environment variable names expected by the backend implementation. Never commit real credentials or secrets.

---

# 13. Instructions for the Frontend Development LLM

You are an experienced senior frontend developer.

Your task is to develop the complete SmartRecruit frontend using React, Vite, JavaScript, and Tailwind CSS.

You must integrate the frontend with the existing FastAPI backend described in this README.

### Your responsibilities

1. Inspect the existing frontend directory before modifying anything.
2. Build the application using a modular and maintainable architecture.
3. Implement authentication and JWT integration.
4. Implement role-based navigation for candidates, recruiters, and administrators.
5. Implement all pages and features corresponding to the existing API routes.
6. Use Axios with a centralized API configuration.
7. Create reusable forms, tables, cards, modals, and navigation components.
8. Connect pages to real backend endpoints.
9. Implement proper loading, error, empty, and success states.
10. Ensure the interface is responsive and professional.
11. Test all available API integrations.
12. Prepare the AI Matching page for future Qdrant and Sentence Transformers integration.

### Implementation order

**Phase 1 — Foundation**

- Configure React and Vite.
- Configure Tailwind CSS.
- Install required dependencies.
- Configure React Router.
- Configure Axios.
- Implement AuthContext.
- Implement protected routes.

**Phase 2 — Authentication**

- Login page.
- Registration page.
- JWT handling.
- Role-based redirection.
- Logout.

**Phase 3 — Shared dashboard layout**

- Sidebar.
- Navbar.
- User profile menu.
- Notifications.
- Responsive layout.

**Phase 4 — Candidate interface**

- Candidate dashboard.
- Candidate profile.
- Browse jobs.
- Job details.
- Apply for a job.
- My applications.

**Phase 5 — Recruiter interface**

- Recruiter dashboard.
- Recruiter profile.
- Company management.
- Job offer management.
- Received applications.
- Application review.
- AI Matching page.

**Phase 6 — Administrator interface**

- Admin dashboard.
- User management.
- Company management.
- Job offer management.
- Application overview.

**Phase 7 — Validation**

- Test all API integrations.
- Test each role separately.
- Test protected routes.
- Test invalid credentials.
- Test expired tokens.
- Test form validation.
- Test empty states.
- Test responsive layouts.

### Critical instructions

- Work with the existing backend. Do not rebuild the backend.
- Do not invent routes or database fields.
- Do not use fake data as a substitute for available API responses.
- Do not assume the AI matching service is ready.
- Do not put all frontend logic inside one large component.
- Do not duplicate API calls across components.
- Do not expose sensitive information.
- Inspect the actual backend files and Swagger documentation to verify response schemas before finalizing integrations.
- If an endpoint is not working, report the issue instead of hiding it with mock data.

### Final expected result

A fully functional SmartRecruit web application with:

- Three role-specific interfaces.
- Secure authentication flow.
- Responsive professional design.
- Complete integration with implemented FastAPI routes.
- CRUD functionality where supported.
- Role-based access and navigation.
- Dashboard statistics.
- A prepared AI Matching interface.

The final application should be ready for the next development phase: integrating the actual AI matching services.

---

## 14. Project Development Roadmap

| Phase | Description | Status |
|---|---|---|
| 1 | Backend project structure | Implemented |
| 2 | MongoDB models and database | Implemented in current development |
| 3 | Authentication and authorization | Implemented |
| 4 | Backend REST API routes | Implemented |
| 5 | React frontend | Next |
| 6 | Frontend/backend integration testing | Pending |
| 7 | CV extraction service | Pending |
| 8 | Embedding service | Pending |
| 9 | Qdrant integration | Pending |
| 10 | AI matching engine | Pending |
| 11 | Advanced analytics and optimization | Pending |
| 12 | Final deployment | Pending |

**SmartRecruit — Connecting talent with opportunity through intelligent recruitment.**
## 12. Development and Execution — Docker

SmartRecruit must run using Docker and Docker Compose.

**Important:** Do not run the backend or frontend directly on the host machine using `uvicorn`, `npm run dev`, or local Python environments as the normal development workflow.

Each application component must run in its own container.

### 12.1 Container Architecture

```text
                  SMARTRECRUIT
                       |
                Docker Compose
                       |
       +---------------+---------------+
       |               |               |
    Frontend         Backend         MongoDB
    React/Vite       FastAPI         Database
       |               |               |
    Port 5173       Port 8000       Port 27017
                       |
             +---------+---------+
             |         |         |
           Qdrant     Redis     Neo4j
             |         |         |
          Port 6333  Port 6379  Port 7474
```

Each service must have its own Docker container.

### 12.2 Recommended Docker Structure

```text
SmartRecruit/
│
├── docker-compose.yaml
├── .env
├── .env.example
├── .gitignore
├── README.md
│
├── backend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── requirements.txt
│   └── app/
│
├── frontend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│
└── volumes/
```

### 12.3 Docker Compose Services

The Docker Compose configuration should define:

| Service | Container responsibility |
|---|---|
| `frontend` | React + Vite application |
| `backend` | FastAPI REST API |
| `mongodb` | Main database |
| `qdrant` | Vector database |
| `redis` | Cache |
| `neo4j` | Graph database |

Requirements:

- Use Docker named volumes for persistent database data.
- Use a dedicated Docker network for internal communication.
- Configure service dependencies and health checks.
- Load configuration through environment variables.
- Never hardcode credentials in Dockerfiles.
- Use container service names for internal communication.

### 12.4 Important Container Networking

Inside Docker, services must communicate using their Compose service names.

For example, the backend should use:

```env
MONGODB_URI=mongodb://mongodb:27017
QDRANT_URL=http://qdrant:6333
REDIS_URL=redis://redis:6379
NEO4J_URI=bolt://neo4j:7687
```

Do not use `localhost` for communication between containers because `localhost` refers to the current container itself.

For the frontend, use a browser-accessible API address or configure a Vite proxy. Do not use `http://backend:8000` directly in browser-side Axios requests because the browser cannot resolve Docker's internal service names.

### 12.5 Running the Application

From the project root:

Build and start all services:

```powershell
docker compose up --build -d
```

Check running containers:

```powershell
docker compose ps
```

View logs:

```powershell
docker compose logs -f
```

View backend logs:

```powershell
docker compose logs -f backend
```

View frontend logs:

```powershell
docker compose logs -f frontend
```

Stop containers:

```powershell
docker compose down
```

Stop containers and delete persistent volumes (destructive):

```powershell
docker compose down -v
```

### 12.6 Accessing Services

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger documentation | http://localhost:8000/docs |
| Qdrant dashboard | http://localhost:6333/dashboard |
| Neo4j Browser | http://localhost:7474 |

MongoDB and Redis are accessed through their containers or database clients.

### 12.7 Frontend Docker Configuration

The frontend must support development inside Docker.

Use Vite configured to listen on:

```text
0.0.0.0
```

Configure Docker volumes and hot reload so frontend changes are reflected without rebuilding the container for every code change.

Use an environment variable or Vite proxy for API communication.

### 12.8 Backend Docker Configuration

The backend must run inside its own container.

Use:

```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

The development command may use `--reload`; production should use an appropriate production configuration.

Ensure that backend dependencies are installed inside the backend image.

### 12.9 Docker Development Rules

1. All application services must run in Docker containers.
2. Do not require local Python or Node.js installations to run the application.
3. Do not run MongoDB locally on Windows.
4. Keep frontend and backend in separate containers.
5. Use Docker Compose for service orchestration.
6. Use named volumes for database persistence.
7. Use Docker service names for internal networking.
8. Configure environment variables through `.env`.
9. Provide `.env.example` without real credentials.
10. Ensure hot reload works during development.
11. Make sure the complete project can start with `docker compose up --build -d`.
12. Do not remove existing backend functionality while configuring Docker.

The final application must be reproducible on another machine with Docker Desktop and Docker Compose installed.