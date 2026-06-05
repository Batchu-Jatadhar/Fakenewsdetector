import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        trust: {
          DEFAULT: "#10B981",
          light: "#34D399",
          dark: "#059669",
        },
        danger: {
          DEFAULT: "#EF4444",
          light: "#F87171",
          dark: "#DC2626",
        },
        uncertain: {
          DEFAULT: "#F59E0B",
          light: "#FBBF24",
          dark: "#D97706",
        },
        surface: {
          DEFAULT: "#1E293B",
          light: "#334155",
          dark: "#0F172A",
        },
      },
    },
  },
  plugins: [],
};
export default config;
