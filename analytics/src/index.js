import ADMIN_HTML from "./admin.html";

const SLUG = /^[a-z0-9-]{1,64}$/;
const LANGS = new Set(["zh", "en"]);
const BOT = /bot|crawl|spider|slurp|preview|headless|lighthouse|curl|wget|python-requests|httpclient/i;
const MAX_SLUGS = 50;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const cors = corsHeaders(request, env);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }

    try {
      if (url.pathname === "/hit" && request.method === "POST") return await hit(request, env, cors);
      if (url.pathname === "/counts" && request.method === "GET") return await counts(url, env, cors);
      if (url.pathname === "/admin" && request.method === "GET") {
        return new Response(ADMIN_HTML, {
          headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" },
        });
      }
      if (url.pathname === "/api/stats" && request.method === "GET") {
        if (!(await authorized(request, env))) return json({ error: "unauthorized" }, 401);
        return json(await stats(url, env), 200, { "cache-control": "no-store" });
      }
      return json({ error: "not found" }, 404, cors);
    } catch (err) {
      console.error(err);
      return json({ error: "server error" }, 500, cors);
    }
  },
};

function allowedOrigins(env) {
  return (env.ALLOWED_ORIGINS || "").split(",").map((s) => s.trim()).filter(Boolean);
}

function corsHeaders(request, env) {
  const origin = request.headers.get("Origin");
  const headers = { Vary: "Origin" };
  if (origin && allowedOrigins(env).includes(origin)) {
    headers["Access-Control-Allow-Origin"] = origin;
    headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS";
    headers["Access-Control-Allow-Headers"] = "Content-Type";
    headers["Access-Control-Max-Age"] = "86400";
  }
  return headers;
}

function json(body, status = 200, headers = {}) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", ...headers },
  });
}

function referrerHost(raw, siteHosts) {
  if (!raw) return null;
  try {
    const host = new URL(raw).hostname.toLowerCase();
    return siteHosts.has(host) ? null : host.slice(0, 120);
  } catch {
    return null;
  }
}

async function hit(request, env, cors) {
  const origin = request.headers.get("Origin");
  if (!origin || !allowedOrigins(env).includes(origin)) return json({ error: "forbidden" }, 403, cors);

  // The client posts text/plain so the browser skips the CORS preflight round trip.
  let body;
  try {
    body = JSON.parse(await request.text());
  } catch {
    return json({ error: "bad request" }, 400, cors);
  }
  const slug = String(body.slug || "");
  if (!SLUG.test(slug)) return json({ error: "bad slug" }, 400, cors);
  const lang = LANGS.has(body.lang) ? body.lang : null;

  const ua = request.headers.get("User-Agent") || "";
  if (!BOT.test(ua)) {
    const cf = request.cf || {};
    const siteHosts = new Set(allowedOrigins(env).map((o) => new URL(o).hostname));
    await env.DB.batch([
      env.DB.prepare(
        "INSERT INTO views (slug, count) VALUES (?1, 1) ON CONFLICT(slug) DO UPDATE SET count = count + 1",
      ).bind(slug),
      env.DB.prepare(
        "INSERT INTO visits (slug, lang, ts, country, region, city, referrer) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)",
      ).bind(
        slug,
        lang,
        new Date().toISOString(),
        cf.country || null,
        cf.region || null,
        cf.city || null,
        referrerHost(body.referrer, siteHosts),
      ),
    ]);
  }

  const row = await env.DB.prepare("SELECT count FROM views WHERE slug = ?1").bind(slug).first();
  return json({ counts: { [slug]: row ? row.count : 0 } }, 200, cors);
}

async function counts(url, env, cors) {
  const slugs = [...new Set((url.searchParams.get("slugs") || "").split(","))]
    .filter((s) => SLUG.test(s))
    .slice(0, MAX_SLUGS);
  const result = Object.fromEntries(slugs.map((s) => [s, 0]));
  if (slugs.length) {
    const placeholders = slugs.map((_, i) => `?${i + 1}`).join(",");
    const { results } = await env.DB.prepare(`SELECT slug, count FROM views WHERE slug IN (${placeholders})`)
      .bind(...slugs)
      .all();
    for (const r of results) result[r.slug] = r.count;
  }
  return json({ counts: result }, 200, { ...cors, "cache-control": "public, max-age=30" });
}

async function authorized(request, env) {
  const token = env.ADMIN_TOKEN;
  const header = request.headers.get("Authorization") || "";
  if (!token || !header.startsWith("Bearer ")) return false;
  const enc = new TextEncoder();
  const [a, b] = await Promise.all([
    crypto.subtle.digest("SHA-256", enc.encode(header.slice(7))),
    crypto.subtle.digest("SHA-256", enc.encode(token)),
  ]);
  return crypto.subtle.timingSafeEqual(a, b);
}

async function stats(url, env) {
  const days = Math.min(Math.max(parseInt(url.searchParams.get("days") || "30", 10) || 30, 1), 365);
  const slug = url.searchParams.get("slug");
  const since = new Date(Date.now() - days * 86400_000).toISOString();
  const tz = env.TZ_OFFSET || "+0 hours";

  const filter = slug && SLUG.test(slug) ? " AND slug = ?2" : "";
  const bind = (stmt, ...extra) => (filter ? stmt.bind(since, slug, ...extra) : stmt.bind(since, ...extra));

  const [articles, regions, referrers, daily, langs] = await Promise.all([
    env.DB.prepare(
      `SELECT v.slug, v.count AS total,
              (SELECT COUNT(*) FROM visits s WHERE s.slug = v.slug AND s.ts >= ?1) AS recent
         FROM views v ORDER BY v.count DESC`,
    ).bind(since).all(),
    bind(env.DB.prepare(
      `SELECT country, region, city, COUNT(*) AS n FROM visits
        WHERE ts >= ?1${filter} GROUP BY country, region, city ORDER BY n DESC LIMIT 200`,
    )).all(),
    bind(env.DB.prepare(
      `SELECT referrer, COUNT(*) AS n FROM visits
        WHERE ts >= ?1${filter} GROUP BY referrer ORDER BY n DESC LIMIT 50`,
    )).all(),
    bind(env.DB.prepare(
      `SELECT date(ts, ?${filter ? 3 : 2}) AS day, COUNT(*) AS n FROM visits
        WHERE ts >= ?1${filter} GROUP BY day ORDER BY day`,
    ), tz).all(),
    bind(env.DB.prepare(
      `SELECT lang, COUNT(*) AS n FROM visits WHERE ts >= ?1${filter} GROUP BY lang ORDER BY n DESC`,
    )).all(),
  ]);

  return {
    days,
    slug: filter ? slug : null,
    articles: articles.results,
    regions: regions.results,
    referrers: referrers.results,
    daily: daily.results,
    langs: langs.results,
  };
}
