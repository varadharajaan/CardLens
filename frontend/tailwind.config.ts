import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/lib/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#0b0f1a",
        panel: "#121829",
        panel2: "#0f1422",
        line: "#1e2740",
        ink: "#e6e9f2",
        muted: "#8a93a8",
        brand: { DEFAULT: "#6366f1", 2: "#a855f7" },
        ok: "#34d399",
        warn: "#fbbf24",
        danger: "#f87171",
        info: "#60a5fa",
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(99,102,241,0.25), 0 18px 50px -20px rgba(99,102,241,0.45)",
      },
      fontFamily: {
        sans: ["var(--font-geist-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-geist-mono)", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};
export default config;
