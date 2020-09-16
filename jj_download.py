import os
import sys
import requests
from concurrent.futures import ThreadPoolExecutor


class JDonwload(object):
    """从网页下载m3u8视频"""

    # 线程池的最大线程数
    MAX_WORKERS = 10  

    def __init__(self, url):
        """根据url初始化一些参数"""
        self.exist_file = 0
        self.folder_name = url.split("/")[-2]
        # m3u8的url链接，建议不要用https
        self.base_url = "/".join(
            [*url.split("/")[:-1], self.folder_name]).replace("https", "http")
        self.url = self.base_url + ".m3u8"
        # 获取视频段的数量，type为string
        respons = requests.get(self.url)
        self.max_munber = respons.text.split(
            "\n")[-3].split("_")[-1].split(".")[0]
        # 创建保存的文件夹
        if not os.path.exists(self.folder_name):
            os.mkdir(self.folder_name)
        full_path = os.path.abspath(self.folder_name)
        self.path1 = os.path.join(full_path, "*.ts")
        self.path2 = os.path.join(full_path, self.folder_name + ".mp4")

    def download_thread(self, url):
        """定义线程中的下载函数，略过已下载文件"""
        file_name = url.split("/")[-1]
        file_name = os.path.join(self.folder_name, file_name)
        if os.path.exists(file_name):
            return
        respons = requests.get(url)
        with open(file_name, "wb") as f:
            for chuck in respons.iter_content(1024):
                f.write(chuck)
        self.show_download_statu()

    def show_download_statu(self):
        """展示下载进度"""
        self.exist_file = len([i for i in os.listdir(
            self.folder_name) if i.split(".")[-1] == "ts"])
        if self.exist_file <= int(self.max_munber):
            print(f"\rdownload {self.exist_file} / {int(self.max_munber) + 1}", end="")
        else:
            print(f"\rdownload {self.exist_file} / {int(self.max_munber) + 1}")

    def download(self):
        """下载的方法"""
        while self.exist_file <= int(self.max_munber):
            # 创建线程池
            pool = ThreadPoolExecutor(max_workers=self.MAX_WORKERS)
            # 提交线程任务
            for i in range(int(self.max_munber) + 1):
                link = self.base_url + "_" + \
                    str(i).zfill(len(self.max_munber)) + ".ts"
                pool.submit(self.download_thread, link)
            pool.shutdown()
        # 所有的ts文件合并为mp4文件并删除原有ts文件
        os.system("copy /b %s %s" % (self.path1, self.path2))
        os.system("del %s" % self.path1)


if __name__ == '__main__':
    # 接受终端的传参，支持多个下载链接
    download_urls = sys.argv[1:]
    for url in download_urls:
        downloader = JDonwload(url)
        downloader.download()
