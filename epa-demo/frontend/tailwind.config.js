/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        epa: {
          blue: '#005ea2',
          green: '#00a91c',
          red: '#e52207',
          yellow: '#ffbe2e'
        }
      }
    },
  },
  plugins: [],
}