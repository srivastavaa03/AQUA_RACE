/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        abyss: {
          950: '#05070B',
          900: '#0A0E15',
          800: '#0F141D',
          700: '#151C28',
          600: '#1C2432',
          500: '#28323F',
        },
        border: {
          DEFAULT: '#1E2733',
          light: '#2A3542',
        },
        cyan: {
          accent: '#3ED6D0',
        },
        signal: {
          amber: '#E0A030',
          red: '#D9534F',
          green: '#4FAE8C',
        },
        ink: {
          100: '#E7ECF1',
          300: '#AEB9C4',
          500: '#7C8896',
          700: '#4C5866',
        },
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', '"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      letterSpacing: {
        wider2: '0.08em',
      },
      boxShadow: {
        none: 'none',
      },
    },
  },
  plugins: [],
}
