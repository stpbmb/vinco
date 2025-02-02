/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './*/templates/**/*.html',
    './static/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        'wine': '#722F37',
        'wine-light': '#A4424D',
        'wine-dark': '#4A1F24',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
