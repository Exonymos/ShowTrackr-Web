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
      '**/migrations/',
      '**/coverage_html_report/',
      'src/watchlist/static/js/htmx.min.js',
      'src/watchlist/static/js/bundle.js',
    ],
  },

  // Configuration for JavaScript files
  {
    files: ['src/watchlist/static/js/app.js'],
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
    files: ['src/watchlist/static/js/app.js'],
    ...eslintPluginPrettierRecommended,
  },
];
