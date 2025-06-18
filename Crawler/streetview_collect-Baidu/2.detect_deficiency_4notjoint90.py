# 检测每个数字有几张
# 按数字的张数进行删除

import os

# 储存图片路径
img_storge = r'D:\streetview\streetview_collect\dir\images'

# 获得所有图片命名的列表
name_list = []
for files in os.listdir(img_storge):
    # print(files)
    name = files.split('_')[0]
    # print(name)
    name_list.append(name)
    # 组合出图片的路径
    img_path = img_storge+ files
print(name_list)

# 统计每个图片出现的次数
dict={}
for key in name_list:
    dict[key]=dict.get(key,0)+1
print(dict)


# 打印键值对
count = 0
for key,value in dict.items():
    # print(key,value)
    if value != 4:
        # 将未拼贴图删除
        try:
            os.remove(img_storge + '/{}_0.jpg'.format(key))
        except:
            pass
        try:
            os.remove(img_storge + '/{}_90.jpg'.format(key))
        except:
            pass
        try:
            os.remove(img_storge + '/{}_180.jpg'.format(key))
        except:
            pass
        try:
            os.remove(img_storge + '/{}_270.jpg'.format(key))
        except:
            pass
        count += 1
print('共有 {} 个街景点不足4张'.format(count))

