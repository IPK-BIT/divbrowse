import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import sveltePreprocess from 'svelte-preprocess';
import { resolve } from 'path';
import replace from '@rollup/plugin-replace';

// https://vitejs.dev/config/
export default defineConfig({
    build: {
        sourcemap: true,
        lib: {
            entry: resolve(__dirname, 'src/main.js'),
            name: 'divbrowse',
            fileName: 'divbrowse',
            formats: ['es'],
        },
    },
    resolve: {
        alias: {
            '@': resolve(__dirname, 'src'),
            //'#root': resolve(__dirname, 'src'),
        }
    },
    plugins: [
        replace({
            'process.env.NODE_ENV': JSON.stringify('production')
        }),
        svelte({
            preprocess: [sveltePreprocess({ typescript: true })],
            emitCss: false
        })
    ],
})
