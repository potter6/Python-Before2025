# 需要如下包 pandas transbigdata geopandas xlrd
import pandas as pd
import transbigdata as tbd
import geopandas as gpd
import xlrd
# ==============================================================
# 参数输入区  输入区域   输入分类名  
# 注意:确保out文件夹有对应的文件夹和文件名  参照data 和 xls_data 的读取路径

ZoneName='黄浦区'

# name='交通设施服务'
# name='金融保险服务'
# name='购物服务'
# name='体育休闲服务'
# name='公共设施'
name=['交通设施服务','金融保险服务','购物服务','体育休闲服务','公共设施']
# ==============================================================

# 读取该区的json文件 以得边界范围
json=gpd.read_file('data\区划json\{}.json'.format(ZoneName))

# 创建一个空的DataFrame
final_data = pd.DataFrame()

for i in range(len(name)):

    # 读取一种方法获得的 .csv文件
    data=pd.read_csv(r'out/{}/{}{}.csv'.format(ZoneName,ZoneName,name[i]))

    # 读取一种方法的 .xls文件
    xls_data = pd.read_excel(r'out/{}/{}{}-高德地图.xls'.format(ZoneName,ZoneName,name[i]))

    # 合并数据
    merged_data = pd.concat([data, xls_data],ignore_index=True)

    # 清除在json边界外的点
    merged_data = tbd.clean_outofshape(merged_data, json, col=['lng', 'lat'])

    # 转换坐标系 GCJ02 -> WGS84
    merged_data['lng'], merged_data['lat'] = tbd.gcj02towgs84(merged_data['lng'], merged_data['lat'])

    # 去重复
    merged_data.drop_duplicates(subset=['名称'], inplace=True)

    # 输出保存
    merged_data.to_csv('out\{}\{}{}_wgs84.csv'.format(ZoneName, ZoneName, name[i]), encoding='utf-8-sig',index=None)

    # 将merged_data附加到final_data上 保留原有的列的格式
    final_data = pd.concat([final_data, merged_data], ignore_index=False)

# 将所有数据保存为一个新文件
final_data.to_csv('out\{}\{}_汇总_wgs84.csv'.format(ZoneName, ZoneName), encoding='utf-8-sig', index=False)


