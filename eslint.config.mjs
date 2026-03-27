// eslint.config.mjs
import globals from 'globals';
import js from '@eslint/js';
import eslintPluginPrettierRecommended from 'eslint-plugin-prettier/recommended';

export default [
    // Global ignores
    {
        ignores: [
            '**/node_modules/',
            '**/.venv/',
            '**/apps/desktop/migrations/',
            '**/coverage_html_report/',
            'apps/desktop/src/core/static/js/htmx.min.js',
            'apps/desktop/src/core/static/js/bundle.js',
        ],
    },

    // Configuration for JavaScript files
    {
        files: ['apps/desktop/src/core/static/js/app.js'],
        ...js.configs.recommended,
        languageOptions: {
            ecmaVersion: 2023,
            sourceType: 'module',
            globals: {
                ...globals.browser,
                htmx: 'readonly',
            },
        },

        rules: {
            // "no-console": "warn",
            // "no-unused-vars": ["warn", { "argsIgnorePattern": "^_" }],
        },
    },

    // Prettier integration
    {
        files: ['apps/desktop/src/core/static/js/app.js'],
        ...eslintPluginPrettierRecommended,
    },
];
