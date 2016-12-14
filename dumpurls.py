import os
import src.database

# Set to True if you want to print the row counts to standard output.
DEBUG = False

if __name__ == "__main__":
    # Selected tags from analysis.
    selected_tags = ["nude", "school uniform", "swimsuit", 
                     "japanese clothes", "dress", "shirt"]
    # Create another list without whitespaces.
    selected_tags_nw = [tag.replace(" ", "_") for tag in selected_tags]
    # Create another list with 'tagname_disjoint' for each tagname.
    selected_tags_dj = [tag.__add__("_disjoint") for tag in selected_tags_nw]
    with src.database.BooruDB() as db:
        # Create temporary views for listing the id's of all selected tags.
        for i in range(len(selected_tags)):
            db.execute("CREATE TEMP VIEW {} AS ".format(selected_tags_nw[i]) +
                       "SELECT view FROM tags JOIN tag ON tags.tag = tag.id " +
                       "WHERE tag.name = '{}'".format(selected_tags[i]))
        if DEBUG:               
            for tag in selected_tags_nw:
                statement = "SELECT COUNT(*) FROM {}".format(tag)
                for row in db.execute(statement):
                    print(tag, row[0])
        # Create temporary views for disjoint sets of id's of the selected tags.
        db.execute("CREATE TEMP VIEW nude_disjoint AS "
                   "SELECT * FROM nude " +
                   "EXCEPT SELECT * FROM dress " +
                   "EXCEPT SELECT * FROM school_uniform " +
                   "EXCEPT SELECT * FROM shirt " +
                   "EXCEPT SELECT * FROM swimsuit " +
                   "EXCEPT SELECT * FROM japanese_clothes")
        db.execute("CREATE TEMP VIEW swimsuit_disjoint AS "
                   "SELECT * FROM swimsuit " +
                   "EXCEPT SELECT * FROM dress " +
                   "EXCEPT SELECT * FROM school_uniform " +
                   "EXCEPT SELECT * FROM shirt " +
                   "EXCEPT SELECT * FROM nude " +
                   "EXCEPT SELECT * FROM japanese_clothes")
        db.execute("CREATE TEMP VIEW japanese_clothes_disjoint AS "
                   "SELECT * FROM japanese_clothes " +
                   "EXCEPT SELECT * FROM school_uniform " +
                   "EXCEPT SELECT * FROM swimsuit " +
                   "EXCEPT SELECT * FROM nude")
        db.execute("CREATE TEMP VIEW dress_disjoint AS "
                   "SELECT * FROM dress " +
                   "EXCEPT SELECT * FROM swimsuit " +
                   "EXCEPT SELECT * FROM school_uniform " +
                   "EXCEPT SELECT * FROM shirt " +
                   "EXCEPT SELECT * FROM nude " +
                   "EXCEPT SELECT * FROM japanese_clothes")
        db.execute("CREATE TEMP VIEW school_uniform_disjoint AS "
                   "SELECT * FROM school_uniform " +
                   "EXCEPT SELECT * FROM dress " +
                   "EXCEPT SELECT * FROM swimsuit " +
                   "EXCEPT SELECT * FROM nude " +
                   "EXCEPT SELECT * FROM japanese_clothes_disjoint")
        db.execute("CREATE TEMP VIEW shirt_disjoint AS "
                   "SELECT * FROM shirt " +
                   "EXCEPT SELECT * FROM japanese_clothes " +
                   "EXCEPT SELECT * FROM swimsuit " +
                   "EXCEPT SELECT * FROM nude " +
                   "EXCEPT SELECT * FROM dress_disjoint " +
                   "EXCEPT SELECT * FROM school_uniform_disjoint")
        if DEBUG:
            print("-" * 80)
            for tag in selected_tags_dj:
                statement = "SELECT COUNT(*) FROM {}".format(tag)
                for row in db.execute(statement):
                    print(tag, row[0])
            print("-" * 80)
        # Filter these tags by aspect ratio and size and print its size.
        for tag in selected_tags_dj:
            if DEBUG:  
                statement = ("SELECT COUNT(view.url) FROM {0} JOIN view ON {0}.view = view.id "
                             "WHERE NOT(xsize < 200 or ysize < 200) "
                             "AND (xsize * 1.0) / (ysize * 1.0) >= 0.5 AND (xsize * 1.0) / (ysize * 1.0) <= 2.0".format(tag))
                for row in db.execute(statement):
                    print(tag, row[0])
            with open("data/" + tag[:4] + "_url.txt", "w") as f:
                statement = ("SELECT view.url, view.id FROM {0} JOIN view ON {0}.view = view.id "
                             "WHERE NOT(xsize < 200 or ysize < 200) "
                             "AND (xsize * 1.0) / (ysize * 1.0) >= 0.5 AND (xsize * 1.0) / (ysize * 1.0) <= 2.0".format(tag))
                for row in db.execute(statement):
                    f.write(row[0] + " " + str(row[1]) + "\n")
