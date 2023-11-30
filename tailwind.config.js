/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["templates/index.html", "templates/similar_users/index.html", "templates/self_listening/index.html"],
  theme: {
    colors: {
      primary: '#335778',
    },
    extend: {},
  },
  plugins: [require("daisyui")],
}

