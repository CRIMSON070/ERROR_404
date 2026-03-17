/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./App.tsx",
    "./index.html",
  ],
  theme: {
    extend: {
      colors: {
        'dark-bg': '#0a1628',
        'dark-card': '#1a2b42',
        'primary-cyan': '#00d4ff',
        'accent-orange': '#ff6b35',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
      }
    },
  },
  plugins: [],
  darkMode: 'class',
}