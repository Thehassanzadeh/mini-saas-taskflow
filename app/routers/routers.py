"""'

✅ Authentication
POST /auth/register # signup (create user)

POST /auth/login # login → access + refresh token

POST /auth/logout # logout (invalidate refresh token)

POST /auth/refresh # refresh access token

📌 نکته:

/users برای CRUD ادمین یا internal باقی می‌مونه
ساخت یوزر عمومی از طریق /auth/register انجام می‌شه
✅ Password Management
POST /auth/password/forgot # request reset password (email)

POST /auth/password/reset # reset password (token)

PUT /auth/password/change # change password (logged-in user)

✅ Email / Account Verification (اختیاری ولی حرفه‌ای)
POST /auth/email/verify # verify email with token

POST /auth/email/resend # resend verification email

✅ Session / Token Info
GET /auth/me # current auth info (id, roles, scopes)

✅ Optional (Advanced – Later)
OAuth (بدون شکستن API)
GET /auth/oauth/{provider} # google, github, …

GET /auth/oauth/{provider}/callback

Token Management
GET /auth/sessions

DELETE /auth/sessions/{session_id}





🔵 1. USER (Self / Profile)

POST /users # create user (signup)

GET /users/me # get current user

PUT /users/me # update current user

DELETE /users/me # delete current user

GET /users/me/teams # list user teams

GET /users/me/projects # list user projects (optional)

GET /users/me/tasks # list tasks assigned to user


🟢 2. TEAM

POST /teams # create team

GET /teams/{team_id} # view team

PUT /teams/{team_id} # update team

DELETE /teams/{team_id} # delete team

Members
GET /teams/{team_id}/users # list team members

POST /teams/{team_id}/users # add user to team

# PUT /teams/{team_id}/users/{user_id} # update role in team

DELETE /teams/{team_id}/users/{user_id} # remove user from team

Team Projects
GET /teams/{team_id}/projects

Team Tasks
GET /teams/{team_id}/tasks


🟡 3. PROJECT

POST /projects

GET /projects/{project_id}

PUT /projects/{project_id}

DELETE /projects/{project_id}

Project Tasks
GET /projects/{project_id}/tasks


🔴 4. TASK
POST /tasks

GET /tasks/{task_id}

PUT /tasks/{task_id}

DELETE /tasks/{task_id}

Assign / Unassign
POST /tasks/{task_id}/assign # assign task to a user

DELETE /tasks/{task_id}/unassign/{user_id} # remove user from task

Additional
GET /tasks/{task_id}/users # list assigned users


⚫ 5. ADMIN (With admin role)
Users
GET /admin/users

GET /admin/users/{user_id}

PUT /admin/users/{user_id}

DELETE /admin/users/{user_id}

Teams
GET /admin/teams

GET /admin/teams/{team_id}

PUT /admin/teams/{team_id}

DELETE /admin/teams/{team_id}

Projects
GET /admin/projects

GET /admin/projects/{project_id}

PUT /admin/projects/{project_id}

DELETE /admin/projects/{project_id}

Tasks
GET /admin/teams/{team_id}/tasks

GET /admin/tasks

GET /admin/tasks/{task_id}

PUT /admin/tasks/{task_id}

DELETE /admin/tasks/{task_id}

"""
