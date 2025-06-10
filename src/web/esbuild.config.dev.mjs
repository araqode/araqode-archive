// Development esbuild config
import { build, context as esbuildContext } from 'esbuild';
import { copyFileSync } from 'fs';

(async () => {
  const ctx = await esbuildContext({
    entryPoints: ['index.jsx'],
    bundle: true,
    outfile: 'dist/bundle.js',
    jsxFactory: 'h',
    jsxFragment: 'Fragment',
    define: { 'process.env.NODE_ENV': '"development"' },
    publicPath: '/web',
    minify: false,
    sourcemap: true,
    format: 'esm',
    target: ['es2020'],
    loader: { '.js': 'jsx', '.jsx': 'jsx' },
  });
  await ctx.watch();
  copyFileSync('index.html', 'dist/index.html');
})();
