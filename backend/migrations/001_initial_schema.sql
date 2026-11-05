-- Review and run this migration in the Supabase SQL Editor.
-- RLS is enabled; add policies only after deciding the exact access rules.
create extension if not exists pgcrypto;

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text,
  email text unique,
  avatar_url text,
  created_at timestamptz not null default now()
);

create table if not exists public.tasks (
  id uuid primary key default gen_random_uuid(),
  title text not null check (char_length(title) between 1 and 160),
  description text,
  created_by uuid not null references public.profiles(id) on delete cascade,
  status text not null default 'pending'
    check (status in ('pending','in_progress','completed')),
  priority text not null default 'medium'
    check (priority in ('low','medium','high')),
  due_date timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.task_assignments (
  task_id uuid not null references public.tasks(id) on delete cascade,
  user_id uuid not null references public.profiles(id) on delete cascade,
  assigned_by uuid not null references public.profiles(id),
  assigned_at timestamptz not null default now(),
  primary key (task_id, user_id)
);

create table if not exists public.activity_logs (
  id uuid primary key default gen_random_uuid(),
  task_id uuid not null references public.tasks(id) on delete cascade,
  actor_id uuid not null references public.profiles(id),
  action text not null,
  details jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

alter table public.profiles enable row level security;
alter table public.tasks enable row level security;
alter table public.task_assignments enable row level security;
alter table public.activity_logs enable row level security;

-- TODO SECURITY: create and test policies for:
-- 1. users can read their own profile and profiles needed for assignment lookup
-- 2. task creators and assigned users can read a task
-- 3. only authorized users can update task status/details
-- 4. only creators/authorized managers can assign users
-- Do not deploy with RLS enabled and no policies if the app needs browser-side access.
