/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#6366F1', // indigo-500
        secondary: '#06B6D4', // cyan-500
      },
      transitionProperty: {
        'width': 'width',
      },
      zIndex: {
        '60': '60',
      }
    },
  },
  plugins: [],
}