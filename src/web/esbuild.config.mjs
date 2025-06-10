// Production esbuild config
import { build } from 'esbuild';
import { copyFileSync } from 'fs';

build({
  entryPoints: ['index.jsx'],
  bundle: true,
  outfile: 'dist/bundle.js',
  jsxFactory: 'h',
  jsxFragment: 'Fragment',
  define: { 'process.env.NODE_ENV': '"production"' },
  publicPath: '/web',
  minify: true,
  sourcemap: false,
  format: 'esm',
  target: ['es2020'],
  loader: { '.js': 'jsx', '.jsx': 'jsx' },
}).then(() => {
  copyFileSync('index.html', 'dist/index.html');
}).catch(() => process.exit(1));
