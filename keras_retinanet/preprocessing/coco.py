"""
Copyright 2017-2018 Fizyr (https://fizyr.com)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import keras_retinanet

import cv2
import os
import numpy as np

from pycocotools.coco import COCO


class CocoGenerator(keras_retinanet.preprocessing.Generator):
    def __init__(self, data_dir, set_name, *args, filter_empty_images=True, **kwargs):
        self.data_dir  = data_dir
        self.set_name  = set_name
        self.coco      = COCO(os.path.join(data_dir, 'annotations', 'instances_' + set_name + '.json'))
        self.image_ids = self.coco.getImgIds()

        if filter_empty_images:
            self.image_ids = [idx for idx in self.image_ids if len(self.coco.getAnnIds(idx, iscrowd=False))]

        self.load_classes()

        super(CocoGenerator, self).__init__(*args, **kwargs)

    def load_classes(self):
        # load class names (name -> label)
        categories = self.coco.loadCats(self.coco.getCatIds())
        categories.sort(key=lambda x: x['id'])

        self.classes             = {}
        self.coco_labels         = {}
        self.coco_labels_inverse = {}
        for c in categories:
            self.coco_labels[len(self.classes)] = c['id']
            self.coco_labels_inverse[c['id']] = len(self.classes)
            self.classes[c['name']] = len(self.classes)

        # also load the reverse (label -> name)
        self.labels = {}
        for key, value in self.classes.items():
            self.labels[value] = key

    def size(self):
        return len(self.image_ids)

    def num_classes(self):
        return len(self.classes)

    def name_to_label(self, name):
        return self.classes[name]

    def label_to_name(self, label):
        return self.labels[label]

    def coco_label_to_label(self, coco_label):
        return self.coco_labels_inverse[coco_label]

    def coco_label_to_name(self, coco_label):
        return self.label_to_name(self.coco_label_to_label(coco_label))

    def label_to_coco_label(self, label):
        return self.coco_labels[coco_label]

    def image_aspect_ratio(self, image_index):
        image = self.coco.loadImgs(self.image_ids[image_index])[0]
        return float(image['width']) / float(image['height'])

    def load_image(self, image_index):
        image = self.coco.loadImgs(self.image_ids[image_index])[0]
        path  = os.path.join(self.data_dir, 'images', self.set_name, image['file_name'])
        return cv2.imread(path)

    def load_annotations(self, image_index):
        # get ground truth annotations
        annotations_ids = self.coco.getAnnIds(imgIds=self.image_ids[image_index], iscrowd=False)

        # some images appear to miss annotations (like image with id 257034)
        if len(annotations_ids) == 0:
            raise ValueError("image with index {} (coco_id: {}) has no annotations".format(image_index, self.image_ids[image_index]))

        # parse annotations
        coco_annotations = self.coco.loadAnns(annotations_ids)
        annotations      = np.zeros((0, 5))
        for idx, a in enumerate(coco_annotations):
            annotation        = np.zeros((1, 5))
            annotation[0, :4] = a['bbox']
            annotation[0, 4]  = self.coco_label_to_label(a['category_id'])
            annotations       = np.append(annotations, annotation, axis=0)

        # transform from [x, y, w, h] to [x1, y1, x2, y2]
        annotations[:, 2] = annotations[:, 0] + annotations[:, 2]
        annotations[:, 3] = annotations[:, 1] + annotations[:, 3]

        return annotations
