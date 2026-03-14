# API Endpoints - Student AI

## Authentication
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/auth/register` | POST | Register a new user account. |
| `/api/auth/login` | POST | Authenticate and start a session. |
| `/api/auth/logout` | POST | End current user session. |

## AI Tasks
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/tasks/generate` | POST | Request AI task completion (Assignment, Solver, etc). |
| `/api/tasks/history` | GET | Retrieve user's previous task history. |
| `/api/tasks/export/<id>` | GET | Export a specific AI response as PDF, DOCX, or TXT. |

## Administration
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/admin/stats` | GET | Retrieve global system usage statistics (Admin only). |
