# robogarden-views

Cloudflare Worker + D1 that counts article reads for the RoboGarden site.

- Live: <https://robogarden-views.worldloop.workers.dev>
- Dashboard: <https://robogarden-views.worldloop.workers.dev/admin> (token in `.admin-token`, git-ignored)
- Each counted visit stores article, time, language, country / region / city (Cloudflare IP geolocation) and referring site. Raw IPs are not stored.
- A page counts once per browser session; known bot user agents are skipped.

| Endpoint | Use |
| --- | --- |
| `POST /hit` | Count one visit, body `{"slug","lang","referrer"}`; only from `ALLOWED_ORIGINS` |
| `GET /counts?slugs=a,b` | Public counts for the site |
| `GET /api/stats?days=30&slug=` | Aggregates for the dashboard, `Authorization: Bearer <token>` |

```bash
npm install
npx wrangler deploy                      # publish code changes
npx wrangler secret put ADMIN_TOKEN      # rotate the dashboard token
npx wrangler d1 execute robogarden-views --remote --command "SELECT * FROM views"
```

Behind the corporate proxy, `d1 execute --file` fails on the upload step; pass SQL with `--command` instead.

The site side lives in `_gen/site/views.js`; `VIEWS_API` in `_gen/site/build_site.py` points the pages at this Worker.
