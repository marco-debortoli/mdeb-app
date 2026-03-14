/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Forest greens — primary brand color (hiking/outdoors)
        forest: {
          50:  '#f2f7ee',
          100: '#e0ecda',
          200: '#c2d9b7',
          300: '#97be8a',
          400: '#6b9f5c',
          500: '#4a7f3d',
          600: '#36642d',
          700: '#2d5027',
          800: '#264220',
          900: '#1f3619',
          950: '#0f1f0d',
        },
        // Earth/stone tones — secondary (cartography, rock)
        earth: {
          50:  '#f7f4ef',
          100: '#ede5d8',
          200: '#d9cab3',
          300: '#c2a885',
          400: '#ae8b60',
          500: '#9b7348',
          600: '#7d5b39',
          700: '#634830',
          800: '#503b28',
          900: '#403023',
          950: '#231910',
        },
        // Slate blues — accent (mountain sky, technology)
        slate: {
          50:  '#f1f4f9',
          100: '#e2e8f2',
          200: '#c5d1e5',
          300: '#9aafd3',
          400: '#6a89be',
          500: '#4a6fa5',
          600: '#3a598a',
          700: '#304870',
          800: '#2b3d5d',
          900: '#28354e',
          950: '#1a2234',
        },
        // Parchment — background (aged map paper)
        parchment: {
          50:  '#fdfcf8',
          100: '#f8f5ee',
          200: '#f0e9d6',
          300: '#e4d4b2',
          400: '#d4b984',
          500: '#c49d5e',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
