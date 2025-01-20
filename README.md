Python app originally created to edit Zed code editor .json files with a color pallete generated from a loaded background image.
This was also a project done while working through the boot.dev coursework.

Loading a theme will generate the theme section will all available options and buttons to choose colors for each from either the current palette or a color chosoer.
Upon loading a theme and colors from options will be loaded into the palette.

Loading an image will generate 20 colors using colorthief at the highest quality setting that colorthief allows and add them to the current palette.
This means you can load an existing theme.json file, load an image you want to use as your background, and add colors to the theme to make it better match your background.

Saving a theme saves both the newly set theme options as well as generates a palette file to save a list of all colors in the theme.

Currently there are some hard coded functions to specifically help with the nested .json format that the Zed themes use. This will be changed in the future to better support theming of other apps.

TO DO:
  Button to randomly assign all values, would be great if this could also be more specific (Generate light theme, dark theme, colorful theme, etc)
  Buttons to load Dark/Light mode skeletons
  Field to be able to type in number of colors you want to pull from image using colorthief.
  ZhemerThemed.py is a work in progress playing with ttk to try to go back through and theme the app.
