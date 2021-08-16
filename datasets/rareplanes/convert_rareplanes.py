import xml.etree.ElementTree as ET
from natsort import natsorted
import glob
import csv
import os

def make_labelfile(dir_images, xml_files, out_csv):
    with open(out_csv, 'a') as f:
        for xml_file in xml_files:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            filename = str(tree.findall("filename")[0].text)
            num_objects = str(tree.findall("num_object_mask_objects")[0].text)
            for e in root.findall('object'):
                category = str(e.findall("category1")[0].text)
                xmin = str(e.findall("bndbox2D/xmin")[0].text)
                ymin = str(e.findall("bndbox2D/ymin")[0].text)
                xmax = str(e.findall("bndbox2D/xmax")[0].text)
                ymax = str(e.findall("bndbox2D/ymax")[0].text)
                # print(dir_images +filename, xmin, ymin, xmax, ymax, category)
                out_list = [dir_images +filename, xmin, ymin, xmax, ymax, category]
                writer = csv.writer(f)
                writer.writerow(out_list)

if __name__ == '__main__':
    rareplane_dir = "/home/elsa/elsa_work/keras-retinanet/datasets/rareplanes/"

    data_mode = ["train", "val", "test"]
    for i in data_mode:
        dir_xml = rareplane_dir + i + "/labels/"
        dir_images = rareplane_dir + i + "/images/"
        out_csv = rareplane_dir + i + "/csv_label/" + i + "_label.csv"
        try:
            os.remove(out_csv)
        except:
            pass
        xml_files = natsorted(glob.glob(dir_xml + "*.xml"))
        make_labelfile(dir_images, xml_files, out_csv)