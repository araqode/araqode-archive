// API helpers for dataset browsing

export function fetchList(path = "") {
  return fetch(`/api/list?path=${encodeURIComponent(path)}`)
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
