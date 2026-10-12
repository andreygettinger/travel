ANDREY PHOTOGRAPHY — QUICK START

1. Extract the ZIP file. Keep all the folders together.
2. Open index.html in Chrome or another browser. Internet is needed for the world map.
3. Click any green country to open its own photography page.
4. To add photos for Japan, copy your JPG, JPEG, PNG, or WebP images into photos/japan/
5. Right-click countries/japan.html and choose Open with > Notepad.
6. Find the line: const photos = [
7. Put your image filenames between the brackets, like this:

const photos = [
  "tokyo.jpg",
  "mount-fuji.jpg",
  "kyoto.jpg",
];

8. Save the HTML file (Ctrl+S), then refresh the country page in Chrome.
9. Repeat for other countries, using the corresponding photos folder and HTML page.

IMPORTANT: Filenames must match exactly, including .jpg/.jpeg/.png and capitalization.
Keep the site folders together. You do not need to install programming software.
The UK is one country. All visited countries have the same green highlight.

Every photos/<country>/ folder contains a PUT_PHOTOS_HERE.txt marker so the folder remains visible when extracting the ZIP. You can delete the marker after adding your photographs.
