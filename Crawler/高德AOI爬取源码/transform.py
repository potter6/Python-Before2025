import math

pi = 3.1415926535897932384626
def Yr(lnglat,b):
    if b!='':
        c=b[0]+b[1]*abs(lnglat[0])
        d=abs(lnglat[1]/b[9])
        d=b[2]+b[3]*d+b[4]*d*d+b[5]*d*d*d+b[6]*d*d*d*d+b[7]*d*d*d*d*d+b[8]*d*d*d*d*d*d
        if 0>lnglat[0]:
            bd=-1*c
        else:
            bd=c
        lnglat[0]=bd
        if 0 > lnglat[0]:
            bd2 = -1 * d
        else:
            bd2 = d
        lnglat[1] = bd2
        return lnglat
    return
def Mecator2BD09(lng,lat):
    lnglat=[0,0]
    Au=[[1.410526172116255E-8, 8.98305509648872E-6, -1.9939833816331, 200.9824383106796, -187.2403703815547,
          91.6087516669843, -23.38765649603339, 2.57121317296198, -0.03801003308653, 1.73379812E7],
         [- 7.435856389565537E-9, 8.983055097726239E-6, -0.78625201886289, 96.32687599759846, -1.85204757529826,
          -59.36935905485877, 47.40033549296737, -16.50741931063887, 2.28786674699375, 1.026014486E7],
         [- 3.030883460898826E-8, 8.98305509983578E-6, 0.30071316287616, 59.74293618442277, 7.357984074871,
          -25.38371002664745, 13.45380521110908, -3.29883767235584, 0.32710905363475, 6856817.37],
         [- 1.981981304930552E-8, 8.983055099779535E-6, 0.03278182852591, 40.31678527705744, 0.65659298677277,
          -4.44255534477492, 0.85341911805263, 0.12923347998204, -0.04625736007561, 4482777.06],
         [3.09191371068437E-9, 8.983055096812155E-6, 6.995724062E-5, 23.10934304144901, -2.3663490511E-4,
          -0.6321817810242, -0.00663494467273, 0.03430082397953, -0.00466043876332, 2555164.4],
         [2.890871144776878E-9, 8.983055095805407E-6, -3.068298E-8, 7.47137025468032, -3.53937994E-6, -0.02145144861037,
          -1.234426596E-5, 1.0322952773E-4, -3.23890364E-6, 826088.5]]
    Sp=[1.289059486E7, 8362377.87, 5591021, 3481989.83, 1678043.12, 0 ]
    lnglat[0]=math.fabs(lng)
    lnglat[1] =abs(lat)
    for d in range(0,6):
        if lnglat[1]>=Sp[d]:
            c=Au[d]
            break
    lnglat=Yr(lnglat,c)
    return lnglat
def BD092WGS84(lnglat):
    #bd09-gcj

    x_pi = 3.14159265358979324 * 3000.0 / 180.0
    pi = 3.1415926535897932384626  # π
    a = 6378245.0  # 长半轴
    ee = 0.00669342162296594323  # 扁率
    x = lnglat[0] - 0.0065
    y = lnglat[1] - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    lnglat[0] = z * math.cos(theta)
    lnglat[1] = z * math.sin(theta)

    dlat = tranlat1(lnglat[0] - 105.0, lnglat[1] - 35.0)
    dlng = tranlng1(lnglat[0] - 105.0, lnglat[1] - 35.0)
    radlat = lnglat[1] / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lnglat[1] + dlat
    mglng = lnglat[0] + dlng
    return [lnglat[0]* 2 - mglng, lnglat[1] * 2 - mglat]
def tranlat1(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret
def tranlng1(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret