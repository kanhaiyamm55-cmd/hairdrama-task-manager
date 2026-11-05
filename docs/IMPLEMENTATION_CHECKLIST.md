# Implementation checklist

- [ ] Configure Supabase project and Google OAuth provider.
- [ ] Implement callback/session handling using `@supabase/ssr`.
- [ ] Add profile upsert after first successful login.
- [ ] Implement Flask bearer-token verification against Supabase Auth.
- [ ] Add authenticated task list/create/update/delete endpoints.
- [ ] Enforce creator/assignee permissions on the server.
- [ ] Add user search and multi-user assignment.
- [ ] Add Gmail API OAuth and notification service.
- [ ] Send notifications only after database transaction succeeds.
- [ ] Add idempotency / duplicate notification protection.
- [ ] Write API and authorization tests.
- [ ] Add RLS policies and test them with separate users.
- [ ] Deploy frontend and backend; configure production environment variables.
- [ ] Record a truthful code walkthrough explaining your own implementation.
