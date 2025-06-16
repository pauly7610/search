/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        "sf-pro": ["var(--font-sf-pro)"],
        "sf-mono": ["var(--font-sf-mono)"],
      },
      colors: {
        system: {
          background: "var(--color-system-background)",
          "background-secondary": "var(--color-system-background-secondary)",
          "background-tertiary": "var(--color-system-background-tertiary)",
          foreground: "var(--color-system-foreground)",
          "foreground-secondary": "var(--color-system-foreground-secondary)",
          "foreground-tertiary": "var(--color-system-foreground-tertiary)",
          border: "var(--color-system-border)",
          separator: "var(--color-system-separator)",
          fill: "var(--color-system-fill)",
          "fill-secondary": "var(--color-system-fill-secondary)",
        },
        ios: {
          blue: "var(--color-blue)",
          green: "var(--color-green)",
          red: "var(--color-red)",
          orange: "var(--color-orange)",
          yellow: "var(--color-yellow)",
          purple: "var(--color-purple)",
          pink: "var(--color-pink)",
          teal: "var(--color-teal)",
          indigo: "var(--color-indigo)",
        },
      },
      spacing: {
        xs: "var(--spacing-xs)",
        sm: "var(--spacing-sm)",
        md: "var(--spacing-md)",
        lg: "var(--spacing-lg)",
        xl: "var(--spacing-xl)",
        "2xl": "var(--spacing-2xl)",
      },
      borderRadius: {
        xs: "var(--radius-xs)",
        sm: "var(--radius-sm)",
        md: "var(--radius-md)",
        lg: "var(--radius-lg)",
        xl: "var(--radius-xl)",
        "2xl": "var(--radius-2xl)",
      },
      boxShadow: {
        "apple-sm": "var(--shadow-sm)",
        "apple-md": "var(--shadow-md)",
        "apple-lg": "var(--shadow-lg)",
        "apple-xl": "var(--shadow-xl)",
      },
      animation: {
        "bounce-gentle": "bounce-gentle 2s infinite",
        "fade-in": "fade-in 0.3s ease-out",
        "slide-up": "slide-up 0.3s ease-out",
      },
      keyframes: {
        "bounce-gentle": {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-4px)" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "slide-up": {
          "0%": { transform: "translateY(100%)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
      },
    },
  },
  plugins: [],
  darkMode: "media",
};