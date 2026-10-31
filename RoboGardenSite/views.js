(() => {
  const api = document.documentElement.dataset.viewsApi;
  if (!api) return;
  const lang = document.documentElement.lang.startsWith("zh") ? "zh" : "en";
  const label = (n) => (lang === "zh" ? `阅读 ${n}` : `${n} ${n === 1 ? "read" : "reads"}`);

  const fill = (counts) => {
    for (const el of document.querySelectorAll("[data-views]")) {
      const n = counts[el.dataset.views];
      if (typeof n === "number" && n > 0) {
        el.textContent = label(n);
        el.hidden = false;
      }
    }
  };
  const get = (path, init) =>
    fetch(api + path, init).then((r) => (r.ok ? r.json() : Promise.reject(r.status)));

  const article = document.querySelector("article[data-slug]");
  if (article) {
    const slug = article.dataset.slug;
    const key = "rg-viewed:" + slug;
    let counted = false;
    try { counted = sessionStorage.getItem(key) === "1"; } catch {}
    const req = counted
      ? get(`/counts?slugs=${encodeURIComponent(slug)}`)
      : get("/hit", {
          method: "POST",
          headers: { "Content-Type": "text/plain" },
          body: JSON.stringify({ slug, lang, referrer: document.referrer }),
          keepalive: true,
        });
    req
      .then((d) => {
        if (!counted) { try { sessionStorage.setItem(key, "1"); } catch {} }
        fill(d.counts);
      })
      .catch(() => {});
    return;
  }

  const slugs = [...new Set([...document.querySelectorAll("[data-views]")].map((el) => el.dataset.views))];
  if (slugs.length) get(`/counts?slugs=${slugs.map(encodeURIComponent).join(",")}`).then((d) => fill(d.counts)).catch(() => {});
})();
