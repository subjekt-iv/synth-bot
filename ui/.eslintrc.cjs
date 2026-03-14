// Ensure the parser and plugin are explicitly required to avoid resolution issues
require('@typescript-eslint/parser');
require('@typescript-eslint/eslint-plugin');

module.exports = {
    root: true,
    env: { browser: true, es2020: true },
    parser: '@typescript-eslint/parser',
    plugins: ['@typescript-eslint', 'react-refresh'],
    extends: [
        'eslint:recommended',
        'plugin:@typescript-eslint/recommended',
        'plugin:react-hooks/recommended',
    ],
    ignorePatterns: ['dist', '.eslintrc.cjs'],
    rules: {
        'react-refresh/only-export-components': [
            'warn',
            { allowConstantExport: true, allowExportNames: ['useSidebar', 'badgeVariants', 'buttonVariants'] },
        ],
    },
};
