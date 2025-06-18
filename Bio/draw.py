import matplotlib.pyplot as plt
from scipy import interpolate
import numpy as np

import matplotlib.font_manager as mpt
zhfont=mpt.FontProperties(fname="C:\\Windows\\Fonts\\Microsoft YaHei UI") #显示中文字体
#网格线
plt.grid(color='y',linestyle='--',linewidth=0.5)
#导入数据
# file = 'data.txt'
file="C:\\Users\\name\\Desktop\\mod.txt"
a = np.loadtxt(file)
# 数组切片
x = a[:,0]  # 取第一列数据
y = a[:,1]  # 取第二列数据
# 进行样条插值
tck = interpolate.splrep(x,y)
xx = np.linspace(min(x),max(x),100)
yy = interpolate.splev(xx,tck,der=0)
print(xx)
# 画图

# plt.plot(x,y,'o',xx,yy)
plt.plot(x,y,'o',xx,yy)
plt.legend(['               ','               '])
plt.axis([-10,370,60,100])
plt.xlabel('') #注意后面的字体属性
plt.ylabel('')
plt.title('')

# 保存图片
plt.savefig('out.jpg')
plt.show()