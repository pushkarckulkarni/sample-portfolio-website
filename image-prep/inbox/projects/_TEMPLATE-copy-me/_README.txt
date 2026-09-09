NEW PROJECT — HOW TO USE THIS FOLDER
============================================================
1. Copy this whole folder and rename the copy to your project,
   using the same pattern as the others:

       13-my-new-house

   The number controls where it appears in the grid. The rest
   becomes the web address: project-13-my-new-house.html

2. Put your photographs in:

       cover.jpg      -> the grid thumbnail   1200x900   (4:3)
       hero.jpg       -> the page banner      2400x1350  (16:9)
       gallery/*.jpg  -> the photo sequence   2000x1333  (3:2)

   Any size, any resolution. They get resized automatically.
   Gallery files are renamed 01.jpg, 02.jpg ... in alphabetical
   order, so name them so they sort correctly.

3. Run:
       python3 image-prep/process.py

4. Copy an existing project.json from website/content/projects/
   into your new folder there, and edit the title, location,
   year, category and text.

5. Run:
       python3 tools/build.py

   The new project page, the grid, and the prev/next links all
   appear on their own. You never touch HTML.
