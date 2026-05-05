/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Adding your "SuperSecure" branding colors
        dark: "#0f172a",
        accent: "#06b6d4",
      }
    },
  },
  plugins: [],
}