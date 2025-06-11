// API helpers for dataset browsing

export function fetchList(urlPrefix, path = "") {
  if (!path) {
    return fetch(`${urlPrefix}/api/list/root.json`).then(r => r.json());
  }
  const url = `${urlPrefix}/api/list/${path}.json`;
  return fetch(url)
    .then(r => r.json());
}

export function fetchTree(urlPrefix, path = "") {
  return fetchList(urlPrefix, path).then(data => {
    return Promise.all(data.items.filter(i => i.is_dir).map(async dir => {
      const child = await fetchTree(urlPrefix, dir.path);
      return { ...child, name: dir.name };
    })).then(children => ({ path, name: '', children }));
  });
}
