**Important: Deep learning part moved to WaifuNet repository.**

Because deep learning seems to be the hot shit atm I'd like to do some experimenting, too.

General idea: Take many labeled images from the Internet and throw them into different neural network architectures.

Step 1: Data aquisition ✓
--------------
Parse [Gelbooru](http://gelbooru.com/) (NSFW).
Idea: Write textual results into SQLite Database. 
* Site Scraper ✓
* Database interface ✓
* Logging system for debugging runtime errors ✓

[The database schema is defined here.](src/create_tables.sql)

Step 2: Data analysis ✓
--------------
Goal: Find promising labels/tags, sizes and other useful attributes.
- Check if data is reliable.
- Find some categories and check their usefulness.
- Filter useless data:
    - Minimal aspect ratio 2:1
    - Minimal size 200x200

[Click here for the current results.](results/README.md)

Step 3: Data preprocessing ✓
--------------
Crop and resize images so that all the images have the same size.

Using the AKAZE feature detector to find a nice window for cropping.
(I don't think it was intended to use feature detection for something like cropping.)

- Target size: 200x200
- Output format: lossless WebP

~~Step 4: Network architecture~~
--------------

~~Step 5: Training and Profiling~~
--------------

Dependencies
--------------
1. Data aquisition
    * beautifulsoup4
    * PyYAML
2. Data analysis
    * jupyter
    * matplotlib
    * numpy
3. Data preprocessing
    * opencv-python (3.1)

Inspiration
--------------
* http://mattya.github.io/chainer-DCGAN/ (source of repo image)
* http://waifu2x.udp.jp/
