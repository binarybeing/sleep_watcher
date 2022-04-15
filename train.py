import numpy as np
from sklearn import svm
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import cv2
import os
import pickle

SHAPE = (100, 100)


def train():

    feature_array, label_array = get_image_data("./trains")
    # 数据的分割
    x_train, x_test, y_train, y_test = train_test_split(
        feature_array, label_array, test_size=0.2, random_state=42)
    shape_info = "shape of raw image data: {0}"
    print(shape_info.format(feature_array.shape))
    print(shape_info.format(x_train.shape))
    print(shape_info.format(x_test.shape))
    # 模型的选择
    clf = svm.SVC(gamma=0.011, C=100., probability=True)
    # 模型的训练
    clf.fit(x_train, y_train)
    # 模型测试
    y_pred = clf.predict(x_test)

    print("pre", y_pred)
    print("test", y_test)
    # 模型保存
    pickle.dump(clf, open("digits_svm.pkl", "wb"))


def get_image_data(directory):
    feature_list = list()
    label_list = list()
    for root, dirs, files in os.walk(directory):
        for d in dirs:
            images = os.listdir(root + "/" + d)
            for image in images:
                label_list.append(d)
                feature_list.append(extract_features_from_image(
                    root + "/" + d + "/" + image))

    return np.asarray(feature_list), np.asarray(label_list)


def extract_features_from_image(image_file):
    img = cv2.imread(image_file)
    img = cv2.resize(img, SHAPE, interpolation=cv2.INTER_AREA)
    img = img.flatten()
    img = img / np.mean(img)
    return img


def test(clf, img_file):
    img = cv2.resize(img_file, SHAPE, interpolation=cv2.INTER_CUBIC)
    img = img.flatten()
    img = img / np.mean(img)
    y_pred = clf.predict(np.reshape(img, (1, 30000)))
    return y_pred


if __name__ == "__main__":
    train()