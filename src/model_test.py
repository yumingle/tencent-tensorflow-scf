# -*- coding:utf-8 -*-
import os
os.environ["CUDA_VISIBLE_DEVICES"]="-1"  
import cv2
import numpy as np
import time

import tensorflow as tf

import os
import sys
from PIL import Image

# labels = load_labels('labels_mobilenet_quant_v1_224.txt')
# Load TFLite model and allocate tensors.
interpreter = tf.lite.Interpreter(model_path="./lite-model_aiy_vision_classifier_food_V1_1.tflite")
interpreter.allocate_tensors()

# Get input and output tensors.
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
print(input_details)
print(output_details)
input_shape = input_details[0]['shape']  # [  1 224 224   3]
# Test model on random input data.
# input_data = np.array(np.random.random_sample(input_shape), dtype=np.uint8)
full_path = '../images/src=http___b-ssl.duitang.com_uploads_item_201609_30_20160930135859_GRFEk.jpeg&refer=http___b-ssl.duitang.jpeg'
img = cv2.imread(full_path, cv2.IMREAD_COLOR )
res_img = cv2.resize(img,(224,224),interpolation=cv2.INTER_CUBIC) 
# 变成长784的一维数据
# new_img = res_img.reshape((224 * 224))

# 增加一个维度，变为 [1, 784]
image_np_expanded = np.expand_dims(res_img, axis=0)
input_data = image_np_expanded#.astype('float32') # 类型也要满足要求
print("Input Image Shape: " + str(input_data.shape))

interpreter.set_tensor(input_details[0]['index'], input_data)

interpreter.invoke()

# The function `get_tensor()` returns a copy of the tensor data.
# Use `tensor()` in order to get a pointer to the tensor.
output_data = interpreter.get_tensor(output_details[0]['index'])

result = np.squeeze(output_data)
#print('result:{}'.format(sess.run(output, feed_dict={newInput_X: image_np_expanded})))
print("Max Value is: " + str(np.max(result)))
# 输出结果是长度为10（对应0-9）的一维数据，最大值的下标就是预测的数字
print('result:{}'.format( (np.where(result==np.max(result)))[0][0]  ))
