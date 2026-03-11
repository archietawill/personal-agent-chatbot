/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#ffffff',
        surface: '#f9fafb',
        text: '#1f2937',
        accent: '#3b82f6',
        success: '#22c55e',
        error: '#ef4444',
        warning: '#eab308',
      },
    },
  },
  plugins: [],
}
