

```python
import sqlite3
import operator
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from functools import reduce
from math import log
```


```python
con = sqlite3.connect("data/gelbooru.db")
cur = con.cursor()
timeformat = "%Y-%m-%d %H:%M:%S"
```


```python
## Create some useful views for the upcoming analysis.
# Create view that counts the tags grouped by its name.
cur.execute("CREATE TEMP VIEW IF NOT EXISTS tag_count AS " +
            "SELECT tag.id AS id, tag.name AS name, COUNT(tags.view) AS count " +
            "FROM tag JOIN tags ON tag.id = tags.tag " +
            "GROUP BY tag.name HAVING tag.name <> '1girl' AND tag.name <> 'solo'")
con.commit()
```

# General information

Tags used for searching: solo, 1girl, -comic, -4koma, -animated, -sound, -webm, -animated gif, -asian, -photo, -3d

## Some simple numbers


```python
cur.execute("SELECT * FROM view ORDER BY id ASC LIMIT 1")
first_entry = cur.fetchone()
cur.execute("SELECT * FROM view ORDER BY id DESC LIMIT 1")
last_entry = cur.fetchone()
cur.execute("SELECT COUNT(*) FROM view")
total_count = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM tag")
tag_count = cur.fetchone()[0]
```


```python
print("Id of first post: {} (from {})".format(first_entry[0], first_entry[1]))
print("Id of last post: {} (from {})".format(last_entry[0], last_entry[1]))
first_post_datetime = datetime.strptime(first_entry[1], timeformat)
last_post_datetime = datetime.strptime(last_entry[1], timeformat)
timedelta = last_post_datetime - first_post_datetime
print("Total count: {} (spanning {} days)".format(total_count, timedelta.days))
print("Number of tags: {}".format(tag_count))
```

    Id of first post: 5 (from 2007-07-16 00:20:00)
    Id of last post: 3150000 (from 2016-04-26 03:00:24)
    Total count: 1212463 (spanning 3207 days)
    Number of tags: 213432



```python
id_diff_dict = dict()
last_row = 0
for row in cur.execute("SELECT id FROM view ORDER BY id ASC"):
    key = row[0] - last_row
    last_row = row[0]
    value = id_diff_dict.setdefault(key, 0)
    id_diff_dict[key] = value + 1
```


```python
id_diff_x, id_diff_y = zip(*sorted(id_diff_dict.items(), key=operator.itemgetter(0)))
plt.bar(range(len(id_diff_x)), [log(y,2) for y in id_diff_y])
plt.xticks(range(0, len(id_diff_x), 15), id_diff_x[::15])
plt.title("Histogram for distance between post ids (logarithmic)")
plt.xlabel("Distance")
plt.ylabel("log(Occurences)")
plt.show()
```


![png](output_9_0.png)


Data seems rather consistent. No outliers.


```python
cur.execute("SELECT rating.name, COUNT(view) FROM rates JOIN rating ON rates.rating = rating.id GROUP BY rating")
dist_ratings = cur.fetchall()
```


```python
plt.pie([x[1] for x in dist_ratings], labels=[x[0] for x in dist_ratings], 
        colors=["cyan", "orange", "red"], autopct='%1.1f%%')
plt.axis('equal')
plt.show()
```


![png](output_12_0.png)


Wow. Seems like there is more safe content than I thought.

# Time series

Watch the data for every full month since the beginning. At the moment this is from Aug 2007 to Mar 2016.


```python
total_months = (last_post_datetime.year - first_post_datetime.year - 1) * 12
total_months += last_post_datetime.month + (12 - first_post_datetime.month) + 1
first_id_of_month = np.empty(total_months, dtype=int)
year = 0
month = 0
index = 0
# Get the first id of each month.
for row in cur.execute("SELECT id, posted FROM view ORDER BY id ASC"):
    date = datetime.strptime(row[1], timeformat)
    if date.year > year:
        year = date.year
        month = 0
    if date.month > month:
        month = date.month
        first_id_of_month[index] = row[0]
        index += 1
```


```python
# Count the number of uploads.
id_range = list(zip(first_id_of_month[0:-1], first_id_of_month[1:]))
count_per_month = []
for i in range(0, total_months - 1):
    ids = tuple((str(id) for id in id_range[i]))
    cur.execute("SELECT COUNT(*) FROM view WHERE id >= ? AND id < ?", ids)
    count_per_month.append(cur.fetchone())
```


```python
# Count only safe uploads (no nudes etc.)
id_range = list(zip(first_id_of_month[0:-1], first_id_of_month[1:]))
count_per_month_safe = []
for i in range(0, total_months - 1):
    ids = tuple((str(id) for id in id_range[i]))
    cur.execute("SELECT COUNT(*) FROM view JOIN rates ON view.id = rates.view " +
                "WHERE view.id >= ? AND view.id < ? AND rates.rating = 1", ids)
    count_per_month_safe.append(cur.fetchone())
```


```python
plt.figure(figsize=(8,4))
plt.plot(count_per_month[1:-1], label="Total uploads")
plt.plot(count_per_month_safe[1:-1], label="Only safe uploads", color="cyan")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
plt.xlabel("Month")
plt.ylabel("Uploads")
plt.show()
```


![png](output_19_0.png)


Again, I think it is rather suprising how much the gap between total uploads and explicit content stays consistant.
I thought the gap would widen with the passing of time.

# Tag analysis

Goal: Find appropriate tags for automatic tagging with neural network.


```python
cur.execute("SELECT tag_count.name, tag_count.count, tag_type.name " +
            "FROM tag_count JOIN categorizes ON tag_count.id = categorizes.tag " +
            "JOIN tag_type ON tag_type.id = categorizes.tag_type " +
            "WHERE count > 20000 ORDER BY count DESC")
top_tags = cur.fetchall()
```


```python
print("{0:10} {1:>35} - {2:>6}".format("TYPE", "TAG NAME", "COUNT"))
print("-------------------------------------------------------")
for entry in top_tags:
    print("{0[2]:10} {0[0]:>35} - {0[1]:6d}".format(entry))
print("IN TOTAL:", len(top_tags), "TAGS")
```

    TYPE                                  TAG NAME -  COUNT
    -------------------------------------------------------
    general                              long hair - 562353
    general                                breasts - 474336
    general                                  blush - 384920
    general                                highres - 367095
    general                                 female - 321347
    general                                  smile - 309188
    general                             short hair - 303731
    general                      looking at viewer - 287483
    copyright                               touhou - 267455
    general                              blue eyes - 240885
    general                             open mouth - 238594
    general                                  skirt - 225126
    general                             thighhighs - 218767
    general                            blonde hair - 211997
    general                               red eyes - 195450
    general                             brown hair - 192029
    general                          large breasts - 183983
    general                      simple background - 182881
    general                              underwear - 175434
    general                                    hat - 172276
    copyright                             original - 159673
    general                                 ribbon - 155983
    general                                panties - 154571
    general                                  navel - 153009
    general                             black hair - 149192
    general                                  dress - 147464
    general                                nipples - 147184
    general                              twintails - 142323
    general                                 gloves - 139614
    general                               cleavage - 134956
    general                       white background - 134941
    general                          hair ornament - 133344
    general                                    bow - 131967
    general                             brown eyes - 131218
    general                                sitting - 119314
    general                             green eyes - 116013
    general                                 bad id - 111259
    general                            animal ears - 110502
    general                         school uniform - 107694
    general                         bare shoulders - 105684
    general                         very long hair - 102968
    general                              blue hair - 100822
    general                                    ass -  92974
    general                                  shirt -  89891
    general                            purple eyes -  88974
    general                                jewelry -  88777
    general                                 weapon -  87582
    general                               swimsuit -  86959
    general                            hair ribbon -  83950
    general                          black legwear -  83617
    general                                   nude -  82642
    copyright                    kantai collection -  79432
    general                            purple hair -  77063
    general                                   tail -  76694
    general                                  pussy -  76364
    general                              pink hair -  73825
    general                                  wings -  72194
    general                            yellow eyes -  69793
    general                               ponytail -  69089
    general                                  boots -  68203
    general                                 flower -  67813
    general                               hair bow -  67745
    general                              absurdres -  67046
    general                               barefoot -  66461
    general                            silver hair -  65438
    general                                  lying -  64607
    general                             green hair -  63056
    general                               standing -  60765
    general                              pantyhose -  60442
    general                       detached sleeves -  60186
    general                                 bikini -  59306
    general                              full body -  58085
    general                               red hair -  57288
    general                           long sleeves -  56393
    general                               hairband -  55938
    general                                midriff -  55157
    general                                  braid -  54520
    general                             monochrome -  54373
    general                               censored -  52685
    general                           looking back -  51870
    general                       japanese clothes -  50709
    general                               serafuku -  49361
    general                                  heart -  48993
    general                                  ahoge -  48572
    general                                   feet -  48299
    general                                  shoes -  48121
    general                                glasses -  46858
    general                           elbow gloves -  46620
    general                               gradient -  46404
    general                                  bangs -  45986
    general                                 thighs -  45839
    general                    gradient background -  45384
    general                                striped -  45246
    copyright                             vocaloid -  45225
    general                           huge breasts -  45060
    general                                    sky -  45018
    general                           open clothes -  44445
    general                                   legs -  43759
    general                             collarbone -  42917
    general                                  sweat -  42710
    general                                necktie -  42276
    general                             upper body -  42172
    general                          white legwear -  41969
    general                             flat chest -  41553
    general                             uncensored -  40613
    general                                  sword -  40582
    general                            spread legs -  40462
    general                         one eye closed -  40024
    general                    translation request -  39817
    general                          erect nipples -  39711
    general                                  tears -  39100
    general                          small breasts -  38509
    general                            eyes closed -  38317
    general                               earrings -  37558
    general                               cat ears -  37377
    general                                 frills -  37227
    general                             white hair -  36739
    general                                     :d -  36695
    general                          white panties -  35750
    general                                   food -  35621
    general                            pointy ears -  35584
    general                          pleated skirt -  34324
    general                         zettai ryouiki -  33885
    general                                 tongue -  33878
    copyright                           idolmaster -  33530
    general                                   fang -  33322
    general                                  socks -  33125
    general                                 choker -  33088
    general                              pink eyes -  32844
    general                              aqua eyes -  32780
    general                                   loli -  32649
    general                                    bra -  32474
    general                                areolae -  32408
    general                                armpits -  32365
    general                                holding -  32219
    character                         hatsune miku -  32183
    general                      alternate costume -  31974
    general                                   wink -  30551
    general                                 sketch -  30210
    general                                 shorts -  30136
    general                                   belt -  30061
    general                                  water -  29784
    general                          short sleeves -  29740
    general                      fingerless gloves -  29229
    general                              pantyshot -  29187
    general                                 lowres -  29138
    general                             no panties -  29068
    general                                 no bra -  28840
    general                                game cg -  28059
    general                            from behind -  28029
    general                                on back -  27967
    general                               hairclip -  27681
    general                                    00s -  27272
    general                                   lips -  26825
    general                                    cum -  26708
    general                             open shirt -  26673
    general                                  horns -  26226
    general                               outdoors -  25762
    general                         character name -  25750
    general                          side ponytail -  25364
    general                            twin braids -  25271
    general                                  cloud -  25083
    general                              aqua hair -  24837
    general                                   star -  24811
    general                                upskirt -  24735
    general                          puffy sleeves -  24541
    general                               cat tail -  23961
    general                                  shiny -  23904
    general                           official art -  23859
    general                             black eyes -  23727
    general                             bunny ears -  23678
    general                                 jacket -  23551
    general                            hair flower -  23517
    general                             high heels -  23276
    general                               cameltoe -  22966
    general                                    bed -  22800
    general                                  scarf -  22737
    general                                  chibi -  22489
    general                                    wet -  22408
    general                                 kimono -  22361
    general                               kneeling -  22275
    general                             bottomless -  22239
    general                                uniform -  22184
    general                                   cape -  22174
    general                                arms up -  22099
    general                             tongue out -  22069
    general                                   bdsm -  21932
    general                              miniskirt -  21870
    general                                   toes -  21788
    general                           white gloves -  21786
    general                                   anus -  21594
    general                                 collar -  21544
    general                            nail polish -  21507
    general                               necklace -  21471
    general                            pussy juice -  21426
    general                            orange hair -  21385
    general                              underboob -  21155
    general                                     :o -  21035
    general                             translated -  20980
    general                                topless -  20933
    general                            cowboy shot -  20915
    general                               lingerie -  20852
    general                            parted lips -  20774
    general                                  armor -  20201
    general                               bracelet -  20174
    general                      multicolored hair -  20142
    IN TOTAL: 206 TAGS



```python
tag_count = np.array([entry[1] for entry in top_tags])
print("Mean:", np.mean(tag_count))
print("Standard derivation:", np.std(tag_count))
```

    Mean: 72823.9223301
    Standard derivation: 80927.2597798



```python
plt.figure(figsize=(8, 4))
plt.plot(range(1, len(tag_count) + 1), tag_count, "bo", markersize=1)
plt.axhspan(np.mean(tag_count), np.mean(tag_count) + np.std(tag_count), alpha=0.3)
plt.ylabel("count")
plt.show()
```


![png](output_26_0.png)


Idea. Define categories by these tags:
* nude
* school uniform
* swimsuit
* japanese clothes
* dress
* shirt (for casual style)

*Check to what extend the id's for these tags are disjoint.*

Maybe use some additional features:
* loli
* cat ears

*These tags do not need to be disjoint.*


```python
selected_tags = ("nude", "school uniform", "swimsuit", "japanese clothes", "dress", "shirt", "loli", "cat ears")
```


```python
# Create views for the tags above.
for tag in selected_tags:
    cur.execute("CREATE TEMP VIEW IF NOT EXISTS {} AS ".format(tag.replace(" ", "_")) +
                "SELECT view FROM tags JOIN tag ON tags.tag = tag.id " +
                "WHERE tag.name = '{}'".format(tag))
con.commit()
```


```python
# Count the specified tags.
print("{0:>20}  {1:>6}".format("Tag name", "Count"))
print("-" * 40)
selected_tag_count = dict()
for tag in selected_tags:
    cur.execute("SELECT COUNT(*) FROM {}".format(tag.replace(" ", "_")))
    selected_tag_count[tag] = cur.fetchone()[0]
    print("{0:>20}: {1:6d}".format(tag, selected_tag_count[tag]))
```

                Tag name   Count
    ----------------------------------------
                    nude:  82642
          school uniform: 107694
                swimsuit:  86959
        japanese clothes:  50709
                   dress: 147464
                   shirt:  89891
                    loli:  32649
                cat ears:  37377



```python
# Count the specified tags with safe content.
print("{0:>20}  {1:>6} (SAFE)".format("Tag name", "Count"))
print("-" * 40)
selected_tag_count_safe = dict()
for tag in selected_tags:
    cur.execute("SELECT COUNT(*) FROM {0} JOIN rates ON {0}.view = rates.view ".format(tag.replace(" ", "_")) +
                "WHERE rates.rating = 1")
    selected_tag_count_safe[tag] = cur.fetchone()[0]
    print("{0:>20}: {1:6d}".format(tag, selected_tag_count_safe[tag]))
```

                Tag name   Count (SAFE)
    ----------------------------------------
                    nude:   2317
          school uniform:  81192
                swimsuit:  50474
        japanese clothes:  40819
                   dress: 126407
                   shirt:  56457
                    loli:      0
                cat ears:  24542


Seems like "loli" is used as some kind of fetish word here. (No safe loli pics! Whats wrong with the world?)


```python
selected_tag_count_sorted = sorted(selected_tag_count.items(), key=operator.itemgetter(1), reverse=True)
x, y1 = zip(*selected_tag_count_sorted)
y2 = [selected_tag_count_safe[tag] for tag in x]
plt.bar(range(0, 2 * len(x), 2), y1)
plt.bar(range(1, 2 * len(x) + 1, 2), y2, color="cyan")
plt.axhline(np.mean(tag_count), color="black")
plt.xticks(range(1, 2 * len(x) + 1, 2), x, rotation=-90)
plt.xlabel("Tag names")
plt.ylabel("Number of posts")
plt.legend(["Mean", "All", "Safe"])
plt.show()
```


![png](output_33_0.png)



```python
# Use ordered tags for further processing.
selected_tags = x
selected_tag_count = y1
```


```python
# Check how disjoint the posts for these tags are.
disjoint_tags = [(x.replace(" ", "_"), y.replace(" ", "_"))
                 for x in selected_tags for y in selected_tags if x != y]
disjoint_tag_count = []
for tags in disjoint_tags:
    cur.execute("SELECT COUNT(*) FROM " +
                    "(SELECT view FROM {} ".format(tags[0]) + 
                     "INTERSECT " +
                     "SELECT view FROM {})".format(tags[1]))
    disjoint_tag_count.append(cur.fetchone()[0])
```


```python
disjoint_tag_array = [disjoint_tag_count[i:][:len(selected_tags) - 1] 
                      for i in range(0, len(disjoint_tag_count), len(selected_tags) - 1)]
disjoint_tag_array = np.array(disjoint_tag_array)
tag1, tag2 = zip(*disjoint_tags)
```


```python
fig = plt.figure(figsize=(len(selected_tags), len(selected_tags)))
for i in range(0, len(selected_tags)):
    ax = fig.add_subplot(2, 4, i + 1)
    bars = ax.bar(range(len(selected_tags) - 1), disjoint_tag_array[i,:] / selected_tag_count[i])
    ax.set_title(tag1[i * (len(selected_tags) - 1)])
    ax.set_xticks(np.arange(len(selected_tags) - 1) + 0.4)
    ax.set_xticklabels(tag2[i * (len(selected_tags) - 1):][:(len(selected_tags) - 1)], rotation=-90)
    ax.set_ylim([0, 0.20])
    r = 0.
    for bar in bars:
        bar.set_color((r, 0, 1 - r))
        r += 0.16
fig.tight_layout()
plt.show()
```


![png](output_37_0.png)


This is the most important plot of this notebook. Here you can see how many images are tagged with another tag than the main tag. That is bad because I want the sets of images to be as disjoint as possible. (Goal: Categorizing instead of automatic tagging.)

### Results

* The **loli** tag seems to be useless. These lolis wear no clothes.
* The **nude** tag is very nice. Most of the time you can count on its correctness.
* **cat ears** are okayish… But this is only a nice extra so I think it is better to not use this tag.
* **japanese clothes** are nice as well.
* As well as **swim suits**.
* And the **dress** tag is suprisingly disjoint, too.
* As expected the **shirt** tag is the most problematic.
* Directly followed by **school uniform**

Firstly, do not use *loli* for *cat ears* any further.

### What to do now

(You should really read about mathematical notation in Jupyter.)

1. nude' := {nude} - ALL
2. swimsuit' := {swimsuit} - ALL
3. japanese' := {japanese clothes} - {nude} - {swimsuit} - {school uniform}
4. dress' := {dress} - ALL
5. school' := {school uniform} - {dress} - {swimsuit} - {nude} - japanese'
6. shirt' := {shirt} - {nude} - dress' - school' - {swimsuit} - {japanese clothes}


```python
# nude'
cur.execute("CREATE TEMP VIEW IF NOT EXISTS nude_filtered AS "
            "SELECT * FROM nude " +
            "EXCEPT SELECT * FROM dress " +
            "EXCEPT SELECT * FROM school_uniform " +
            "EXCEPT SELECT * FROM shirt " +
            "EXCEPT SELECT * FROM swimsuit " +
            "EXCEPT SELECT * FROM japanese_clothes")
con.commit()
```


```python
# swimsuit'
cur.execute("CREATE TEMP VIEW IF NOT EXISTS swimsuit_filtered AS "
            "SELECT * FROM swimsuit " +
            "EXCEPT SELECT * FROM dress " +
            "EXCEPT SELECT * FROM school_uniform " +
            "EXCEPT SELECT * FROM shirt " +
            "EXCEPT SELECT * FROM nude " +
            "EXCEPT SELECT * FROM japanese_clothes")
con.commit()
```


```python
# japanese'
cur.execute("CREATE TEMP VIEW IF NOT EXISTS japanese_filtered AS "
            "SELECT * FROM japanese_clothes " +
            "EXCEPT SELECT * FROM school_uniform " +
            "EXCEPT SELECT * FROM swimsuit " +
            "EXCEPT SELECT * FROM nude")
con.commit()
```


```python
# dress'
cur.execute("CREATE TEMP VIEW IF NOT EXISTS dress_filtered AS "
            "SELECT * FROM dress " +
            "EXCEPT SELECT * FROM swimsuit " +
            "EXCEPT SELECT * FROM school_uniform " +
            "EXCEPT SELECT * FROM shirt " +
            "EXCEPT SELECT * FROM nude " +
            "EXCEPT SELECT * FROM japanese_clothes")
con.commit()
```


```python
# 'school
cur.execute("CREATE TEMP VIEW IF NOT EXISTS school_filtered AS "
            "SELECT * FROM school_uniform " +
            "EXCEPT SELECT * FROM dress " +
            "EXCEPT SELECT * FROM swimsuit " +
            "EXCEPT SELECT * FROM nude " +
            "EXCEPT SELECT * FROM japanese_filtered")
con.commit()
```


```python
# shirt'
cur.execute("CREATE TEMP VIEW IF NOT EXISTS shirt_filtered AS "
            "SELECT * FROM shirt " +
            "EXCEPT SELECT * FROM japanese_clothes " +
            "EXCEPT SELECT * FROM swimsuit " +
            "EXCEPT SELECT * FROM nude " +
            "EXCEPT SELECT * FROM dress_filtered " +
            "EXCEPT SELECT * FROM school_filtered")
con.commit()
```


```python
filtered_view_names = ("nude_filtered", "swimsuit_filtered", "japanese_filtered",
                       "dress_filtered", "school_filtered", "shirt_filtered")
count_current = []
for name in filtered_view_names:
    cur.execute("SELECT COUNT(*) FROM {}".format(name))
    count_current.append(cur.fetchone()[0])
```


```python
print("Sum:", sum(count_current))
print("Filter small images with sizes on x or y axis < 200.")
print("Filter images with weird aspect ratio < 2:1.")
count_current_filtered = []
for name in filtered_view_names:
    cur.execute("SELECT COUNT({0}.view) FROM {0} JOIN view ON {0}.view = view.id ".format(name) +
                "WHERE NOT(xsize < 200 or ysize < 200) " +
                "AND (xsize * 1.0) / (ysize * 1.0) >= 0.5 AND (xsize * 1.0) / (ysize * 1.0) <= 2.0")
    count_current_filtered.append(cur.fetchone()[0])
print("Filtered sum:", sum(count_current_filtered))
```

    Sum: 524821
    Filter small images with sizes on x or y axis < 200.
    Filter images with weird aspect ratio < 2:1.
    Filtered sum: 511706



```python
fig = plt.figure(figsize=(9,3))
labels = ["Nude", "Swimsuit", "Japanese Clothes", "Dress", "School Uniform", "Shirt"]
ax1 = fig.add_subplot(121)
ax1.pie(count_current, labels=labels, autopct=lambda x: 
        str(int(x / 100. * sum(count_current))) + "\n" + "({:.2g}%)".format(x))
ax2 = fig.add_subplot(122)
ax2.pie(count_current_filtered, labels=labels, autopct=lambda x: 
        str(int(x / 100. * sum(count_current))) + "\n" + "({:.2g}%)".format(x))
ax1.axis("equal")
ax2.axis("equal")
plt.show()
```


![png](output_47_0.png)

