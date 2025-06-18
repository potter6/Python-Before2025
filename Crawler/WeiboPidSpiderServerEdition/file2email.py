import os
import zipfile
import yagmail
import datetime
import time

namefile = 'Tempzip'

def zipDir(dirpath, outFullName, zip_limit_size):
    """
    压缩指定文件夹并限制每个压缩包的大小
    :param dirpath: 目标文件夹路径
    :param outFullName: 压缩文件保存路径+xxxx.zip
    :param zip_limit_size: 单个压缩包限制大小（字节）
    """
    zip_index = 1
    current_zip_size = 0
    zip_file = zipfile.ZipFile(f"{outFullName}_{zip_index}.zip", "w", zipfile.ZIP_DEFLATED)

    for path, dirnames, filenames in os.walk(dirpath):
        for filename in filenames:
            file_path = os.path.join(path, filename)
            file_size = os.path.getsize(file_path)

            # 检查当前压缩包是否超出限制
            if current_zip_size + file_size > zip_limit_size:
                zip_file.close()  # 关闭当前压缩包
                zip_index += 1   # 更新压缩包索引
                current_zip_size = 0  # 重置当前大小
                zip_file = zipfile.ZipFile(f"{outFullName}_{zip_index}.zip", "w", zipfile.ZIP_DEFLATED)  # 新建压缩包

            zip_file.write(file_path, os.path.relpath(file_path, dirpath))  # 添加文件
            current_zip_size += file_size  # 更新当前压缩大小

    zip_file.close()  # 压缩完成，关闭压缩包


if __name__ == "__main__":
    # 清除Tempzip文件夹里的所有文件
    for root, dirs, files in os.walk(namefile, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    namefile = 'Tempzip'
    emailhost = "smtp.qq.com"
    emailname = "473161189@qq.com"
    emailpassword = "hspxxpupkwowbggg"  # 授权码 需要到邮箱的设置里面 开启授权

    # 新建一个打包的文件夹，如果已存在则删除新加
    if os.path.exists(namefile):
        os.rmdir(namefile)

    os.mkdir(namefile)

    input_path = "./sqlite"
    output_path = namefile + '/hhhsqlite'
    zip_limit_size = 100 * 1024 * 1024  # 假设每个压缩包限制为30MB

    # 压缩文件夹
    zipDir(input_path, output_path, zip_limit_size)

    # 创建客户端
    yag = yagmail.SMTP(
        user=emailname,
        password=emailpassword,
        host=emailhost,
        smtp_ssl=True
    )

    # 发送所有生成的压缩包
    zip_index = 1
    while True:
        zip_file_name = f"{output_path}_{zip_index}.zip"
        if not os.path.exists(zip_file_name):  # 如果没有更多文件可发送
            break

        # 发送邮件
        yag.send(
            to=emailname,
            subject='为什么要演奏春日影？ '+str(zip_index),
            contents=f'哈喽，你好！\n\n这是你的爬虫sqlite文件分布式传输,现在是 {datetime.datetime.now()}\n来自腾讯云OrcaTerm',
            attachments=[zip_file_name]
        )
        print(str(zip_index)+'的编号完成啦')
        # time.sleep(20)  # 延迟X秒，避免发送过快被服务器拒绝
        zip_index += 1  # 发送下一个压缩包

    # 关闭 yagmail 客户端
    yag.close()

    # 清除Tempzip文件夹里的所有文件
    for root, dirs, files in os.walk(namefile, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
