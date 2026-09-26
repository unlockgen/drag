# Global leaderboard setup

Local leaderboard is functional now. Global is NOT deployed yet.

This Python 3 server provides shared SQLite storage without third-party packages.
Deploy it on a server with a persistent disk and an HTTPS reverse proxy. GitHub Pages cannot execute it.

1. Set `LEADERBOARD_DB` to a persistent path, such as `/data/leaderboard.sqlite3`.
2. Set `ALLOWED_ORIGIN=https://unlockgen.github.io` and `PORT=8080`.
3. Run `python3 leaderboard-server/server.py`. Put HTTPS and per-client rate limiting in front of it. Back up the SQLite database.
4. Set `window.CHURCHRACERS_LEADERBOARD_API` in `leaderboard-config.js` to its HTTPS origin, without a trailing path.
5. Bump the cache version in `sw.js`, commit and let GitHub Pages deploy.
6. Post a clean score from one device and verify it appears on a second device.

The app posts only when the player presses POST MY BEST TO GLOBAL. Names, countries and scores become public. A random anonymous bearer token identifies a browser; the database stores its hash. Clearing browser storage loses that identity. Names aren't reserved; different browsers can use the same name.

Only clean scores from this update onward are recorded locally; older stats have no racer/format metadata and aren't imported. Local rankings can be lost when browser data is cleared. Scores remain client-reported practice results and can be fabricated; this is not suitable for prizes or verified competitions. Accounts, server-authoritative race sessions and abuse controls would be needed for that.

Routes: POST /players, GET /scores?mode=sportsman (or pro), POST /scores with Bearer token and JSON `{name,country,mode,ms}`. Minimum score per token and tree format is retained. SQL is parameterized, score input is validated and writes are rate-limited.
