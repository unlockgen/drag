# Activate the Supabase leaderboard

Project: `ldcafrdfyswiynampfne`.

1. In Supabase SQL Editor, create a new query, paste the entire contents of `migrations/20260926232000_leaderboard.sql`, and Run.
2. Under Authentication → Sign In / Providers, enable Anonymous Sign-Ins and save.
3. Open https://unlockgen.github.io/drag/?v=supabase1, select Global in Leaderboards. It should show an empty ranking rather than an error.
4. Set a clean time, then choose POST MY BEST TO GLOBAL. Verify the score from a second browser.

The public anon API key in leaderboard-config.js is intentionally browser-visible. Do not substitute a service_role or secret key.

RLS is enabled. Only public score columns are selectable. Direct inserts/updates/deletes are revoked; the authenticated crj_submit function validates inputs, obtains the player ID from auth.uid(), rate-limits submissions per user, and keeps their best score per format. Anonymous Auth creates a browser identity; clearing browser storage loses it. Names are not unique or reserved. Scores are client-reported practice times, not verified competition results. Consider CAPTCHA and account-based anti-abuse before running public prizes.

The previous Python leaderboard-server is an alternative and is not used by this Supabase client. No separate Python hosting is needed.
