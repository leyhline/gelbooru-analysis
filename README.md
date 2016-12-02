Because deep learning seems to be the hot shit atm I'd like to do some experimenting, too.

General idea: Take many labeled images from the Internet and throw them into different neural network architectures.

Step 1: Data aquisition
--------------
Parse [Gelbooru](http://gelbooru.com/) (NSFW).
1. Write textual results into SQLite Database.
    * Site Scraper *(finished)*
    * Database interface *(finished)*
    * Logging system for debugging runtime errors *(finished)*
2. Data analysis: Find promising labels/tags, sizes and other useful attributes.
3. Download appropriate images.
4. (Optional) Preprocessing of images. (Greyscale, Crop, Resizing)

Step 2: Network architecture
--------------
Use TensorFlow. (Yuck! Google!)
And read a lot of papers/tutorials.

Ideas: 
* My own [Deepdreaming](https://en.wikipedia.org/wiki/Deepdreaming) Network.
* Image recognition/ automatic labeling.
* Generating networks for my very own AI generated Waifu.

Step 3: Training and Profiling
--------------
Or: How to find a PC with Nvidia GPU which is fast enough for processing all this data.

Dependencies
--------------
1. Data aquisition
    * beautifulsoup4