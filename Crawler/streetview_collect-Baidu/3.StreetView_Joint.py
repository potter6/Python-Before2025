import os
from PIL import Image
import glob

# 原街景图的路径
original_path = r'./dir/images'
# 拼接街景图的路径
joint_path = r'./dir/images_joint'

name_list = []
for fn in os.listdir(original_path):
    name_list.append(fn)
# print(name_list)

# 获得已经存在的所有街景图片FID
exist_FID = glob.glob1(joint_path, "*.jpg")
exist_FID = [i.split('.')[0] for i in exist_FID]

for images in [name_list[i:i + 4] for i in range(0, len(name_list), 4)]:
    # print(images)
    # 对4个图片的顺序进行排序, 影响最后的拼接效果
    images = [images[0], images[3], images[1], images[2]]
    # 打开第一张
    images1 = images[0]
    # 判断已经采集的跳过
    if images1.split('.')[0] in exist_FID:
        print(images1,"已经处理")
        continue

    image1_open = Image.open(original_path + '/' + images1)
    # 获取图像尺寸
    width, height = image1_open.size
    # 创建空白长图
    white = Image.new(image1_open.mode, (width * 4, height))
    # 依次打开图像, 进行拼接
    for j, image in enumerate(images):
        image_open = Image.open(original_path + '/' + image)
        # 拼接图像
        white.paste(image_open, box=(j * width, 0))
    print(images1.split('_')[0],'处理完成')
    white.save(joint_path + '/' + images1.split('_')[0] + '.jpg', quality=80)



