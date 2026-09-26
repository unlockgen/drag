begin;
create table if not exists public.crj_scores (
 user_id uuid not null references auth.users(id) on delete cascade,
 mode text not null check (mode in ('sportsman','pro')),
 name text not null check (char_length(name) between 1 and 24),
 country text not null check (country in ('JM','US','GB','CA','TT','BB','OTHER')),
 ms integer not null check (ms between 0 and 1800),
 updated_at timestamptz not null default now(),
 primary key (user_id, mode)
);
alter table public.crj_scores enable row level security;
revoke all on public.crj_scores from anon, authenticated;
grant select (mode,name,country,ms) on public.crj_scores to anon, authenticated;
drop policy if exists crj_public_rankings on public.crj_scores;
create policy crj_public_rankings on public.crj_scores for select to anon, authenticated using (true);
create index if not exists crj_scores_ranking on public.crj_scores(mode,ms);
create or replace function public.crj_submit(p_name text,p_country text,p_mode text,p_ms integer)
returns void language plpgsql security definer set search_path = '' as $$
declare uid uuid := auth.uid();
begin
 if uid is null then raise exception 'Sign in required'; end if;
 if p_name is null or char_length(trim(p_name)) not between 1 and 24 or p_name ~ '[[:cntrl:]]'
 or p_country is null or p_country not in ('JM','US','GB','CA','TT','BB','OTHER')
 or p_mode is null or p_mode not in ('sportsman','pro')
 or p_ms is null or p_ms not between 0 and 1800 then raise exception 'Invalid score'; end if;
 perform pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtextextended(uid::text,0));
 if exists(select 1 from public.crj_scores where user_id=uid and updated_at > now()-interval '3 seconds') then
 raise exception 'Please wait a few seconds before posting again'; end if;
 insert into public.crj_scores as scores(user_id,mode,name,country,ms) values(uid,p_mode,trim(p_name),p_country,p_ms)
 on conflict(user_id,mode) do update set name=excluded.name,country=excluded.country,ms=least(scores.ms,excluded.ms),updated_at=now();
end $$;
revoke all on function public.crj_submit(text,text,text,integer) from public, anon;
grant execute on function public.crj_submit(text,text,text,integer) to authenticated;
commit;
