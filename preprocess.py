import os
import random
import shutil
from os import listdir
import json
import sys

# get the path of the directory that contains the images
ROOT = sys.argv[1]
if ROOT[-1] == "/":
    ROOT = ROOT[:-1]

width = 1920
height = 1080

TARGET_PATH = ROOT + "_data"
os.makedirs(TARGET_PATH, exist_ok=True)

filelist = []

for root, dirs, files in os.walk(ROOT):
	for file in files:
        #append the file name to the list
		filelist.append(os.path.join(root,file))


def get_file_name(file_path):
    return os.path.splitext(os.path.basename(file_path))[0]

labels = list() # json's
images = list() # images
names_without_ext = list() # names without extension

check1 = list()
check2 = list()
for file in filelist:
    if file.endswith(".json"):
        check1.append(get_file_name(file))
        labels.append(file)
    elif file.endswith(".jpg"):
        check2.append(get_file_name(file))
        images.append(file)
    else:
        continue


if set(check1) != set(check2) or len(check1) != len(check2):
    print("Something is wrong")
    os._exit(0)


os.makedirs(os.path.join(TARGET_PATH, "img"), exist_ok=True)
os.makedirs(os.path.join(TARGET_PATH, "json"), exist_ok=True)

for file in images:
    shutil.copy(file, os.path.join(TARGET_PATH, "img"))

for file in labels:
    shutil.copy(file, os.path.join(TARGET_PATH, "json"))


modes = ["train", "val", "test", "train_ann", "val_ann", "test_ann"]
for mode in modes:
     os.makedirs(os.path.join(TARGET_PATH, mode), exist_ok=True)



# getting class names
class_name_path = os.path.join(TARGET_PATH, "json")
files_for_class = [f for f in listdir(class_name_path)]


category = list()
for file in files_for_class:
    with open(os.path.join(class_name_path, file), 'r') as class_curr_file:
        class_curr = json.load(class_curr_file)
    class_categories = class_curr['annotations']
    for i in range(len(class_categories)):
        class_id = class_categories[i]['category_id']
        class_status = class_categories[i]['status']
        if class_status != 'normal' and class_status != 'abnormal':
            continue
        class_name = class_curr['categories'][class_id-1]['supercategory'] + '_' + class_curr['categories'][class_id-1]['name'] + '-' + class_status
        category.append(class_name)

category = list(set(category))
num_classes = len(category)

cat = dict()
for i in range(len(category)):
    cat[str(category[i])] = i

    
# create data.yaml file in TARGET_PATH
with open(os.path.join(TARGET_PATH, "data.yaml"), 'w') as f:
    f.write("path: " + TARGET_PATH)
    f.write("\n\n")
    f.write("train: train")
    f.write("\n")
    f.write("val: val")
    f.write("\n")
    f.write("test: test")
    f.write("\n\n")
    f.write("nc: " + str(num_classes))
    f.write("\n")
    f.write("names: " + str(category))

    f.close()


# lets make folders in main directory
# os.makedirs(PATH)

files_n = [f for f in listdir(os.path.join(TARGET_PATH, "json"))]
files_without_suffix = [f.split(".")[0] for f in files_n]

splitter = {'train': [], 'val': [], 'test': []}
splitter_img = {'train': [], 'val': [], 'test': []}
splitter_json = {'train': [], 'val': [], 'test': []}
tv = int(len(files_without_suffix)*0.8) #train to val
vt = int(len(files_without_suffix)*0.9) #val to test

random.seed(1000)
random.shuffle(files_without_suffix)

for i in range(len(files_without_suffix)):
    if i<tv:
        splitter["train"].append(files_without_suffix[i])
        splitter_img["train"].append(files_without_suffix[i]+".jpg")
        splitter_json["train"].append(files_without_suffix[i]+".json")
    elif i<vt:
        splitter["val"].append(files_without_suffix[i])
        splitter_img["val"].append(files_without_suffix[i]+".jpg")
        splitter_json["val"].append(files_without_suffix[i]+".json")
    else:
        splitter["test"].append(files_without_suffix[i])
        splitter_img["test"].append(files_without_suffix[i]+".jpg")
        splitter_json["test"].append(files_without_suffix[i]+".json")


for file in splitter["train"]:
    shutil.move(TARGET_PATH + "/img/" + file + ".jpg", TARGET_PATH + "/train/")
    shutil.move(TARGET_PATH + "/json/" + file + ".json", TARGET_PATH + "/train_ann/")

for file in splitter["val"]:
    shutil.move(TARGET_PATH + "/img/" + file + ".jpg", TARGET_PATH + "/val/")
    shutil.move(TARGET_PATH + "/json/" + file + ".json", TARGET_PATH + "/val_ann/")

for file in splitter["test"]:
    shutil.move(TARGET_PATH + "/img/" + file + ".jpg", TARGET_PATH + "/test/")
    shutil.move(TARGET_PATH + "/json/" + file + ".json", TARGET_PATH + "/test_ann/")


shutil.rmtree(TARGET_PATH + "/img/")
shutil.rmtree(TARGET_PATH + "/json/")




for mode in ["train", "val", "test"]:
    mypath = TARGET_PATH + "/" + mode + "/"
    mypath_label = TARGET_PATH + "/" + mode + "_ann/"
    files = [f for f in listdir(mypath)]
    files_without_suffix = [f.split(".")[0] for f in files]


    labeling = {}
    for i in range(len(files_without_suffix)):
        labeling[files_without_suffix[i]] = i

    for file in files_without_suffix: 
        wrt = open(mypath + file + ".txt", "w")
        width = width
        height = height
        with open(mypath_label + file + '.json', 'r') as curr_file:
            curr = json.load(curr_file)
        list_img = curr['annotations']
        for i in range(len(list_img)):
            curr_img = list_img[i]
            st = ''
            if curr_img['polygon'] == []: 
                id = curr_img['category_id']
                status = curr_img['status']
                if status != 'normal' and status != 'abnormal':
                    continue
                name = curr['categories'][id-1]['supercategory'] + '_' + curr['categories'][id-1]['name'] + '-' + status

                if name not in cat:
                    print('ERROR')
                    print(file)
                    print('ERROR')
                
                category_id = cat[name]
                curr_bbox = curr_img['bbox']
                bbox = [curr_bbox[0], curr_bbox[1], curr_bbox[2], curr_bbox[3]]

                bbox[0] = max(bbox[0], 0)
                bbox[0] = min(bbox[0], width)
                bbox[1] = max(bbox[1], 0)
                bbox[1] = min(bbox[1], height)
                bbox[2] = max(bbox[2], 0)
                bbox[2] = min(bbox[2], width)
                bbox[3] = max(bbox[3], 0)
                bbox[3] = min(bbox[3], height)

                center_x = (bbox[0] + bbox[2]/2)/width
                center_y = (bbox[1] + bbox[3]/2)/height
                w = bbox[2]/width
                h = bbox[3]/height

            else:
                id = curr_img['category_id']
                status = curr_img['status']
                if status != 'normal' and status != 'abnormal':
                    continue
                name = curr['categories'][id-1]['supercategory'] + '_' + curr['categories'][id-1]['name'] + '-' + status
            
                if name not in cat:
                    print('ERROR')
                    print(file)
                    print('ERROR')
                
                category_id = cat[name]

                curr_segm = curr_img["polygon"]
                
                n = len(curr_segm)
                coor_x = []
                coor_y = []
                for i in range(n):
                    if i % 2 == 0:
                        coor_x.append(curr_segm[i])
                    else:
                        coor_y.append(curr_segm[i])
                
                x_min = max(min(coor_x), 0)
                x_max = min(max(coor_x), width)
                y_min = max(min(coor_y), 0)
                y_max = min(max(coor_y), height)

                center_x = (x_min+x_max)/(2*width)
                center_y = (y_min+y_max)/(2*height)
                w = (x_max-x_min)/width
                h = (y_max-y_min)/height

            st = str(category_id) + ' ' + str(center_x) + ' ' + str(center_y) + ' ' + str(w) + ' ' + str(h) + '\n'
            wrt.write(st)
        