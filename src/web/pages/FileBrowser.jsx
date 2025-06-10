import { h } from 'preact';
import { useEffect, useState } from 'preact/hooks';
import { fetchTree, fetchList } from '../api/dataset.js';

function FolderTree({ node, onSelect, currentPath }) {
  if (!node || !Array.isArray(node.children)) return null; 
    return (
    <ul style={{ listStyle: 'none', paddingLeft: 16 }}>
      {node.children.map(child => (
        <li key={child.path}>
          <span
            style={{ cursor: 'pointer', fontWeight: currentPath === child.path ? 'bold' : 'normal' }}
            onClick={() => onSelect(child.path)}
          >
            📁 {child.name}
          </span>
          <FolderTree node={child} onSelect={onSelect} currentPath={currentPath} />
        </li>
      ))}
    </ul>
  );
}

export default function FileBrowser() {
  const [items, setItems] = useState([]);
  const [path, setPath] = useState("");
  const [fileUrl, setFileUrl] = useState(null);
  const [isImage, setIsImage] = useState(false);
  const [tree, setTree] = useState(null);

  useEffect(() => {
    fetchList(path).then(data => setItems(data.items));
  }, [path]);

  useEffect(() => {
    fetchTree().then(setTree);
  }, []);

  function open(item) {
    if (item.is_dir) setPath(item.path);
    else {
      setFileUrl(`/dataset/${item.path}`);
      setIsImage(/\.(png|jpg|jpeg|gif|bmp|webp)$/i.test(item.name));
    }
  }

  function goUp() {
    setFileUrl(null);
    setIsImage(false);
    setPath(path.split('/').slice(0, -1).join('/'));
  }

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <aside style={{ width: 260, borderRight: '1px solid #ddd', padding: 12, overflowY: 'auto' }}>
        <h3>Folders</h3>
        <FolderTree node={tree} onSelect={p => { setPath(p); setFileUrl(null); setIsImage(false); }} currentPath={path} />
      </aside>
      <main style={{ flex: 1, padding: 24 }}>
        <h2>Dataset Browser</h2>
        {path && <button onClick={goUp}>Up</button>}
        {!fileUrl ? (
          <ul>
            {items.map(item => (
              <li key={item.path}>
                <button onClick={() => open(item)}>
                  {item.is_dir ? '📁' : '📄'} {item.name}
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <div>
            {isImage ? (
              <img src={fileUrl} alt="preview" style={{maxWidth:'100%'}} />
            ) : (
              <a href={fileUrl} download>Download file</a>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
