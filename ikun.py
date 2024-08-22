import argparse
import os
import cv2
import subprocess
from cv2 import VideoWriter_fourcc
import numpy as np
import requests
import time
from PIL import Image, ImageFont, ImageDraw
import pygame

Abs_Dir_Path = os.path.dirname(os.path.abspath(__file__))

class Video2CodeVideo:

    
    def __init__(self):
        # 配置字典
        self.config_dict = {
            "input_file": "test.mp4",
            "cache_dir": os.path.join(Abs_Dir_Path, "cache"),
            "save_cache_flag": True,
            "ascii_char_list": list("01B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:oa+>!:+. "),
        }
        # 创建cache文件夹
        self.create_cache_dir()
        # 检查网络状况
        self.check_network()
        # 获取命令行参数
        self.config_dict.update(self.get_args().__dict__)
        # 获取命令行参数
    def get_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--input_file", type=str, default="./assets/test.mp4")
        #parser.add_argument("--cache_dir", type=str, default=os.path.join(Abs_Dir_Path, "/cache"), help="cache")
        parser.add_argument("--save_cache_flag", type=bool, default=True)
        parser.add_argument("--use_gpu", type=bool, default=False)
        parser.add_argument("--use_mp3", type=bool, default=False)
        return parser.parse_args()

    def create_cache_dir(self):
        if not os.path.exists(self.config_dict["cache_dir"]):
            os.mkdir(self.config_dict["cache_dir"])
    # 检查网络状况
    def check_network(self):
        try:
            requests.get('http://www.baidu.com', timeout=1)
        except requests.ConnectionError as e:
            # 使用pygame播放MP3
            pygame.mixer.init()
            pygame.mixer.music.load(Abs_Dir_Path + '/error.mp3')
            pygame.mixer.music.play()
            time.sleep(1)
            exit()
        else:
            pass
    
    # 下载文件
    url_cloud = None
    # def download_mp4(self, url):
    #     requests.get(url=url_cloud, stream=True)
    # 第一步，从函数将像素转换为字符
    def rgb_2_char(self, r, g, b, alpha=256):
        if alpha == 0:
            return ''
        length = len(self.config_dict["ascii_char_list"])
        gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b)
        unit = (256.0 + 1) / length
        return self.config_dict["ascii_char_list"][int(gray / unit)]
 
    # 第一步，从函数将txt转换为图片
    def txt_2_image(self, file_name):
        im = Image.open(file_name).convert('RGB')
        raw_width = im.width
        raw_height = im.height
        width = int(raw_width / 6)
        height = int(raw_height / 15)
        im = im.resize((width, height), Image.NEAREST)

        txt = ""
        colors = []
        for i in range(height):
            for j in range(width):
                pixel = im.getpixel((j, i))
                colors.append((pixel[0], pixel[1], pixel[2]))
                if len(pixel) == 4:
                    txt += self.rgb_2_char(pixel[0], pixel[1], pixel[2], pixel[3])
                else:
                    txt += self.rgb_2_char(pixel[0], pixel[1], pixel[2])
            txt += '\n'
            colors.append((255, 255, 255))

        im_txt = Image.new("RGB", (raw_width, raw_height), (255, 255, 255))
        dr = ImageDraw.Draw(im_txt)

        # 尝试使用具体的字体文件
        try:
            font = ImageFont.load_default()  # 使用合适的字体文件和大小
        except IOError:
            font = ImageFont.load_default()
            print("字体加载失败，使用默认字体")

        # 获取单个字符的尺寸
        try:
            bbox = font.getbbox('A')
            font_h = bbox[3] - bbox[1]
            font_w = bbox[2] - bbox[0]
        except Exception as e:
            print(f"获取字体尺寸失败: {e}")
            font_h, font_w = 10, 10  # 备用尺寸，确保后续操作不失败

        print(f"font_h: {font_h}, font_w: {font_w}")  # 调试输出

        font_h = int(font_h * 1.5)  # 确保 font_h 是整数
        font_w = int(font_w * 1.5)  # 确保 font_w 是整数

        x, y = 0, 0  # 初始化 x 和 y

        for i in range(len(txt)):
            if txt[i] == '\n':
                x += font_h
                y = 0
            dr.text((y, x), txt[i], fill=colors[i])
            y += font_w

        name = file_name
        im_txt.save(name)

    
    # 第一步，将视频转换为字符图片
    def video_2_txt_jpg(self, file_name):
        vc = cv2.VideoCapture(file_name)
        c = 1
        if vc.isOpened():
            r, frame = vc.read()
            if not os.path.exists(self.config_dict["cache_dir"]):
                os.mkdir(self.config_dict["cache_dir"])
            os.chdir(self.config_dict["cache_dir"])
        else:
            r = False
        while r:
            cv2.imwrite(str(c) + '.jpg', frame)
            self.txt_2_image(str(c) + '.jpg')  # 同时转换为ascii图
            r, frame = vc.read()
            c += 1
        os.chdir('..')
        return vc
    
    # 第二步，将字符图片合成新视频
    def txt_jpg_2_video(self, outfile_name, fps):
        fourcc = VideoWriter_fourcc(*"MJPG")
 
        images = os.listdir(self.config_dict["cache_dir"])
        im = Image.open(self.config_dict["cache_dir"] + '/' + images[0])
        vw = cv2.VideoWriter(outfile_name + '.avi', fourcc, fps, im.size)
 
        os.chdir(self.config_dict["cache_dir"])
        for image in range(len(images)):
            frame = cv2.imread(str(image + 1) + '.jpg')
            vw.write(frame)
 
        os.chdir('..')
        vw.release()
 
    # 第三步，从原视频中提取出背景音乐
    def video_extract_mp3(self, file_name):
        outfile_name = file_name.split('.')[0] + '.mp3'
        subprocess.call('ffmpeg -i ' + file_name + ' -f mp3 -y ' + outfile_name, shell=True)
 
    # 第四步，将背景音乐添加到新视频中
    def video_add_mp3(self, file_name, mp3_file):
        outfile_name = file_name.split('.')[0] + '-txt.mp4'
        subprocess.call('ffmpeg -i ' + file_name + ' -i ' + mp3_file + ' -strict -2 -f mp4 -y ' + outfile_name, shell=True)
 
    # 第五步，如果没配置保留则清除过程文件
    def clean_cache_while_need(self):
        def remove_cache_dir(path):
            if os.path.exists(path):
                if os.path.isdir(path):
                    dirs = os.listdir(path)
                    for d in dirs:
                        if os.path.isdir(path + '/' + d):
                            remove_cache_dir(path + '/' + d)
                        elif os.path.isfile(path + '/' + d):
                            os.remove(path + '/' + d)
                    os.rmdir(path)
                    return
                elif os.path.isfile(path):
                    os.remove(path)
                return
        def delete_middle_media_file():
            os.remove(self.config_dict["input_file"].split('.')[0] + '.mp3')
            os.remove(self.config_dict["input_file"].split('.')[0] + '.avi')
        if not self.config_dict["save_cache_flag"]:
            remove_cache_dir(self.config_dict["cache_dir"])
            delete_middle_media_file()
 
    # 程序主要逻辑
    def main_logic(self):
        # 第一步，将原视频转成字符图片
        print("第一步,正在将原视频转成字符图片")
        vc = self.video_2_txt_jpg(self.config_dict["input_file"])
        # 获取原视频帧率
        fps = vc.get(cv2.CAP_PROP_FPS)
        print("获取原视频帧率:")
        print(fps)
        vc.release()
        print("已将原视频转成字符图片\n")
        # 第二步，将字符图片合成新视频
        print("第二步,正在将字符图片合成新视频")
        self.txt_jpg_2_video(self.config_dict["input_file"].split('.')[0], fps)
        print(self.config_dict["input_file"], self.config_dict["input_file"].split('.')[0] + '.mp3')
        print("已将字符图片合成新视频\n")
        # 第三步，从原视频中提取出背景音乐
        print("第三步, 正在从原视频中提取出背景音乐")
        self.video_extract_mp3(self.config_dict["input_file"])
        print("已从原视频中提取出背景音乐\n")
        # 第四步，将背景音乐添加到新视频中
        print("第四步, 正在将背景音乐添加到新视频中")
        self.video_add_mp3(self.config_dict["input_file"].split('.')[0] + '.avi', self.config_dict["input_file"].split('.')[0] + '.mp3')
        print("已将背景音乐添加到新视频中\n")
        # 第五步，如果没配置保留则清除过程文件
        self.clean_cache_while_need()
        print("字符视频制作完毕\n字符视频为test-txt.mp4\n")
        print("按任意键结束")
        input()

if __name__ == '__main__':
    obj = Video2CodeVideo()
    obj.main_logic()
