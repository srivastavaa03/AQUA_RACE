/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        // Deep-water command console palette. "hull" = near-black navy
        // structural surfaces, "deck" = raised panel surfaces, "chart"
        // = the base a nautical chart sits on, "sonar" = the operative
        // cyan used for live/active data, "flare" = amber for
        // warnings/attention, "hazard" = red for confirmed spill state.
        hull: {
          950: '#070B10',
          900: '#0B121A',
          800: '#111B26',
          700: '#182633',
        },
        deck: {
          800: '#152029',
          700: '#1C2A36',
          600: '#25384A',
          500: '#33495D',
        },
        chart: {
          line: '#2A3F52',
        },
        sonar: {
          400: '#5EEAD4',
          500: '#2DD4BF',
          600: '#14B8A6',
        },
        flare: {
          400: '#FBBF6B',
          500: '#F5A524',
        },
        hazard: {
          400: '#FB7185',
          500: '#E23B4E',
        },
        mist: {
          100: '#E7EDF2',
          300: '#AEBECC',
          500: '#7A8FA3',
          700: '#4C6072',
        },
      },
      fontFamily: {
        sans: ['"Inter"', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', '"JetBrains Mono"', 'monospace'],
      },
      boxShadow: {
        panel: '0 1px 0 0 rgba(255,255,255,0.04) inset, 0 8px 24px -12px rgba(0,0,0,0.6)',
      },
      backgroundImage: {
        grid: 'linear-gradient(rgba(94,234,212,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(94,234,212,0.05) 1px, transparent 1px)',
      },
      backgroundSize: {
        grid: '28px 28px',
      },
      animation: {
        sweep: 'sweep 3.2s linear infinite',
        pulseDot: 'pulseDot 2s ease-in-out infinite',
      },
      keyframes: {
        sweep: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
        pulseDot: {
          '0%, 100%': { opacity: 1, transform: 'scale(1)' },
          '50%': { opacity: 0.55, transform: 'scale(0.85)' },
        },
      },
    },
  },
  plugins: [],
}
