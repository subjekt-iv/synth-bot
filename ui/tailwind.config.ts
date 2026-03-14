import type { Config } from 'tailwindcss'
import typography from '@tailwindcss/typography'

export default {
    darkMode: 'class',
    content: [
        './index.html',
        './src/**/*.{ts,tsx}',
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: [
                    'Inter',
                    'ui-sans-serif',
                    'system-ui',
                    'sans-serif',
                ],
            },
            colors: {
                background: 'hsl(var(--background))',
                foreground: 'hsl(var(--foreground))',
                card: {
                    DEFAULT: 'hsl(var(--card))',
                    foreground: 'hsl(var(--card-foreground))',
                },
                popover: {
                    DEFAULT: 'hsl(var(--popover))',
                    foreground: 'hsl(var(--popover-foreground))',
                },
                primary: {
                    DEFAULT: 'hsl(var(--primary))',
                    foreground: 'hsl(var(--primary-foreground))',
                },
                secondary: {
                    DEFAULT: 'hsl(var(--secondary))',
                    foreground: 'hsl(var(--secondary-foreground))',
                },
                muted: {
                    DEFAULT: 'hsl(var(--muted))',
                    foreground: 'hsl(var(--muted-foreground))',
                },
                accent: {
                    DEFAULT: 'hsl(var(--accent))',
                    foreground: 'hsl(var(--accent-foreground))',
                },
                destructive: {
                    DEFAULT: 'hsl(var(--destructive))',
                    foreground: 'hsl(var(--destructive-foreground))',
                },
                border: 'hsl(var(--border))',
                input: 'hsl(var(--input))',
                ring: 'hsl(var(--ring))',
                sidebar: {
                    DEFAULT: 'hsl(var(--sidebar-background))',
                    foreground: 'hsl(var(--sidebar-foreground))',
                    primary: 'hsl(var(--sidebar-primary))',
                    'primary-foreground': 'hsl(var(--sidebar-primary-foreground))',
                    accent: 'hsl(var(--sidebar-accent))',
                    'accent-foreground': 'hsl(var(--sidebar-accent-foreground))',
                    border: 'hsl(var(--sidebar-border))',
                    ring: 'hsl(var(--sidebar-ring))',
                },
            },
            borderRadius: {
                lg: 'var(--radius)',
                md: 'calc(var(--radius) - 2px)',
                sm: 'calc(var(--radius) - 4px)',
            },
            keyframes: {
                typing: {
                    '0%, 100%': { transform: 'translateY(0)', opacity: '0.5' },
                    '50%': { transform: 'translateY(-2px)', opacity: '1' },
                },
                'loading-dots': {
                    '0%, 100%': { opacity: '0' },
                    '50%': { opacity: '1' },
                },
                wave: {
                    '0%, 100%': { transform: 'scaleY(1)' },
                    '50%': { transform: 'scaleY(0.6)' },
                },
                blink: {
                    '0%, 100%': { opacity: '1' },
                    '50%': { opacity: '0' },
                },
                'text-blink': {
                    '0%, 100%': { color: 'var(--primary)' },
                    '50%': { color: 'var(--muted-foreground)' },
                },
                'bounce-dots': {
                    '0%, 100%': { transform: 'scale(0.8)', opacity: '0.5' },
                    '50%': { transform: 'scale(1.2)', opacity: '1' },
                },
                'thin-pulse': {
                    '0%, 100%': { transform: 'scale(0.95)', opacity: '0.8' },
                    '50%': { transform: 'scale(1.05)', opacity: '0.4' },
                },
                'pulse-dot': {
                    '0%, 100%': { transform: 'scale(1)', opacity: '0.8' },
                    '50%': { transform: 'scale(1.5)', opacity: '1' },
                },
                'shimmer-text': {
                    '0%': { backgroundPosition: '150% center' },
                    '100%': { backgroundPosition: '-150% center' },
                },
                'wave-bars': {
                    '0%, 100%': { transform: 'scaleY(1)', opacity: '0.5' },
                    '50%': { transform: 'scaleY(0.6)', opacity: '1' },
                },
                shimmer: {
                    '0%': { backgroundPosition: '200% 50%' },
                    '100%': { backgroundPosition: '-200% 50%' },
                },
                'spinner-fade': {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
            },
            animation: {
                typing: 'typing 1s ease-in-out infinite',
                'loading-dots': 'loading-dots 1.4s ease-in-out infinite',
                wave: 'wave 1.2s ease-in-out infinite',
                blink: 'blink 1s ease-in-out infinite',
                'text-blink': 'text-blink 2s ease-in-out infinite',
                'bounce-dots': 'bounce-dots 1.4s ease-in-out infinite',
                'thin-pulse': 'thin-pulse 2s ease-in-out infinite',
                'pulse-dot': 'pulse-dot 1.5s ease-in-out infinite',
                'shimmer-text': 'shimmer-text 3s ease-in-out infinite',
                'wave-bars': 'wave-bars 1.2s ease-in-out infinite',
                shimmer: 'shimmer 8s ease-in-out infinite',
                'spinner-fade': 'spinner-fade 1s linear infinite',
            },
        },
    },
    plugins: [typography],
} satisfies Config
