/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./scripts/**/*.py",
    "./app.py"
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "surface-container": "#e2e4ea",
        "primary": "#6366f1",
        "on-primary-container": "#e0e2ff",
        "surface-container-highest": "#d6d8de",
        "on-tertiary-container": "#3b1f63",
        "error-container": "#fee2e2",
        "error": "#dc2626",
        "on-primary-fixed": "#1e1b4b",
        "on-tertiary-fixed": "#2e1065",
        "surface-dim": "#d4d6dc",
        "on-surface": "#2e3040",
        "surface-container-high": "#dcdee4",
        "secondary-container": "#d8dae6",
        "primary-fixed": "#e0e2ff",
        "surface-container-lowest": "#f0f2f8",
        "secondary-fixed-dim": "#b8baca",
        "inverse-surface": "#2e3040",
        "primary-fixed-dim": "#a5b4fc",
        "tertiary-container": "#a78bfa",
        "surface-variant": "#dcdee4",
        "tertiary-fixed-dim": "#c4b5fd",
        "on-secondary-container": "#585a68",
        "on-primary-fixed-variant": "#4338ca",
        "on-error-container": "#991b1b",
        "on-secondary": "#ffffff",
        "on-tertiary-fixed-variant": "#5b21b6",
        "tertiary-fixed": "#ede9fe",
        "on-tertiary": "#ffffff",
        "on-surface-variant": "#585a68",
        "surface-tint": "#6366f1",
        "inverse-on-surface": "#e8eaf0",
        "secondary": "#6c6e7e",
        "on-background": "#2e3040",
        "on-secondary-fixed": "#1a1b26",
        "on-primary": "#ffffff",
        "on-error": "#ffffff",
        "surface-bright": "#edeef4",
        "surface": "#e8eaf0",
        "surface-container-low": "#e5e7ed",
        "on-secondary-fixed-variant": "#404252",
        "tertiary": "#7c3aed",
        "secondary-fixed": "#d8dae6",
        "primary-container": "#818cf8",
        "background": "#e8eaf0",
        "outline-variant": "#d0d2dc",
        "outline": "#8a8c9a",
        "inverse-primary": "#a5b4fc"
      },
      borderRadius: {
        "DEFAULT": "0.5rem",
        "lg": "1rem",
        "xl": "1.5rem",
        "full": "9999px"
      },
      fontFamily: {
        "headline": ["Plus Jakarta Sans"],
        "display": ["Plus Jakarta Sans"],
        "body": ["Plus Jakarta Sans"],
        "label": ["Plus Jakarta Sans"]
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/container-queries')
  ],
}
