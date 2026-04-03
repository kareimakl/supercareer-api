# SuperCareer API Documentation

Welcome to the SuperCareer API. Below is a summary of the available endpoints for the Frontend Team.

## Interactive API Console (Swagger UI)
The easiest way to interact with and test all these endpoints is through our live Swagger dashboard.
- **Swagger UI**: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- **Data Schema (ReDoc)**: [http://localhost:8000/api/redoc/](http://localhost:8000/api/redoc/)
- **Raw OpenAPI YAML**: `schema.yml` (available in the root directory for Postman import).

---

## 1. Authentication & Users
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/register/` | Register a new user | No |
| `POST` | `/api/login/` | Login (Returns Access & Refresh Tokens) | No |
| `POST` | `/api/auth/google/login/` | Login via Google OAuth token | No |
| `POST` | `/api/auth/google/register/` | Register via Google OAuth token | No |
| `POST` | `/api/logout/` | Blacklist the current refresh token | Yes |
| `POST` | `/api/token/refresh/` | Get a new access token using a refresh token | No |
| `POST` | `/api/forgot-password/` | Send OTP for password recovery | No |
| `POST` | `/api/verify-otp/` | Verify the recovery OTP | No |
| `POST` | `/api/reset-password/` | Set new password after OTP verification | No |

## 2. Profile Management
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/profile/` | Fetch current user's profile and skills | Yes |
| `PATCH` | `/api/profile/` | Update profile information and skills | Yes |
| `POST` | `/api/change-password/` | Change password while logged in | Yes |
| `GET` | `/api/accounts/dashboard-stats/` | Get dashboard statistics (matches, proposals) | Yes |

## 3. Opportunities (Jobs & Projects)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/opportunities/jobs/` | List all available full-time jobs | No |
| `GET` | `/api/opportunities/projects/` | List all available freelance projects | No |
| `POST` | `/api/opportunities/refresh-projects/` | Trigger the web scraper to fetch new opportunities | Yes |

## 4. Proposals
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/opportunities/proposals/` | Submit a new proposal to a job/project | Yes |

## 5. AI Matching System
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/matching/` | Get personalized job/project matches using AI vector search | Yes |

---
## Authentication Usage
For endpoints that require authentication (`Auth Required = Yes`), please include the access token in the HTTP Header like this:
```http
Authorization: Bearer <your_access_token>
```
