/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["templates/index.html"],
  theme: {
    colors: {
      primary: '#335778',
    },
    extend: {},
  },
  plugins: [require("daisyui")],
}

