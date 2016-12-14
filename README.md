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

**Important:** If you want to run you own analysis [you need to unpack the database first](data/README.md).

Step 3: Network architecture
--------------
Use TensorFlow. (Yuck! Google!)
And read a lot of papers/tutorials.

Ideas: 
* My own [Deepdreaming](https://en.wikipedia.org/wiki/Deepdreaming) Network.
* Image recognition/ automatic labeling.
* Generating networks for my very own AI generated Waifu.

Step 4: Training and Profiling
--------------
Or: How to find a PC with Nvidia GPU which is fast enough for processing all this data.
1. Download appropriate images.
2. (Optional) Preprocessing of images. (Greyscale, Crop, Resizing)
3. Feed them into the NN and wait.

Idea: Use pool computers for training. 
Save images at some online storage and dynamically load them (in e.g. 100 MB batches) for training.

Dependencies
--------------
1. Data aquisition
    * beautifulsoup4
    * PyYAML
2. Data analysis
    * jupyter
    * matplotlib

Inspiration
--------------
* http://mattya.github.io/chainer-DCGAN/ (source of repo image)
* http://waifu2x.udp.jp/
