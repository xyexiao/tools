from concurrent.futures import ThreadPoolExecutor
import requests
import os

# 线程池的最大线程数
max_workers = 10
# m3u8的url链接
url = ""
base_url = url[:-5]
folder_name = url.split("/")[-1].split(".")[0]

# 获取视频段的数量
respons = requests.get(url)
max_munber = respons.text.split("\n")[-3].split("_")[-1].split(".")[0]
# 创建保存的文件夹
if not os.path.exists(folder_name):
    os.mkdir(folder_name)


def download(url):
    # 定义线程中的下载函数
    file_name = url.split("/")[-1]
    file_name = os.path.join(folder_name, file_name)
    if os.path.exists(file_name):
        return
    respons = requests.get(url)
    with open(file_name, "wb") as f:
        for chuck in respons.iter_content(1024):
            f.write(chuck)

# 创建线程池
pool = ThreadPoolExecutor(max_workers=max_workers)
# 提交线程任务
for i in range(int(max_munber) + 1):
    link = base_url + "_" + str(i).zfill(len(max_munber)) + ".ts"
    pool.submit(download, link)
pool.shutdown()

# 所有的ts文件合并为mp4文件并删除原有ts文件
full_path = os.path.abspath(folder_name)
path1 = os.path.join(full_path, "*.ts")
path2 = os.path.join(full_path, folder_name + ".mp4")
os.system("copy /b %s %s" % (path1, path2))
os.system("del %s" % path1)
