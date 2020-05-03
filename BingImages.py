# `coding:utf-8
'''
https://www.bing.com/HPImageArchive.aspx?
idx=0&          #起始序号
n=8&            #图片总数，最多为8
format=js&      #返回数据格式
pid=HpEdgeAn&   
mkt=zh-cn
'''
import requests
import os
import shutil


baseURL = "https://www.bing.com"
API = "https://www.bing.com/HPImageArchive.aspx?idx=%d&n=%d&format=js"
# 这个API通过调整参数可以总共获取15张图片信息


def getImageInfo(respons_json):
    # 获取响应的json数据中图片的信息
    images = []
    for info in respons_json["images"]:
        images.append({
            "title": info["copyright"].split("©")[0][:-2] + ".jpg",
            "url": baseURL + info["url"]
        })
    return images


def downloadImage(url, save_dir, title):
    # 下载图片
    respons = requests.get(url)
    with open(os.path.join(save_dir, title), "wb") as f:
        for chunk in respons.iter_content(1024):
            f.write(chunk)


def main(images_number=15, save_dir="", cover=False):
    # images_number:下载的图片数量，最多为15
    # save_dir: 图片保存的完整文件夹路径
    # cover: 是否删除文件夹中原有的文件
    respons = requests.get(API % (0, 7))
    images = getImageInfo(respons.json())
    respons = requests.get(API % (7, 8))
    images += getImageInfo(respons.json())
    if save_dir:
        if not os.path.isabs(save_dir):
            raise Exception("保存路径应为完整路径")
        if not os.path.isdir(save_dir):
            raise Exception("保存路径不存在")
        if cover:
            shutil.rmtree(save_dir)
            os.mkdir(save_dir)
    else:
        save_dir = os.path.join(os.getcwd(), "BingImages")
        if not os.path.isdir(save_dir):
            os.mkdir(save_dir)
        if cover:
            shutil.rmtree(save_dir)
            os.mkdir(save_dir)
    for image in images[:images_number]:
        downloadImage(image["url"], save_dir, image["title"])

if __name__ == '__main__':
    main(cover=True)
