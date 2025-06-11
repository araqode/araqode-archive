// API helpers for dataset browsing

export function fetchList(path = "") {
  if (!path) {
    return fetch(`/api/list/root.json`).then(r => r.json());
  }
  const url = `/api/list/${path}.json`;
  return fetch(url)
    .then(r => r.json());
}

export function fetchTree(path = "") {
  return fetchList(path).then(data => {
    return Promise.all(data.items.filter(i => i.is_dir).map(async dir => {
      const child = await fetchTree(dir.path);
      return { ...child, name: dir.name };
    })).then(children => ({ path, name: '', children }));
  });
}
