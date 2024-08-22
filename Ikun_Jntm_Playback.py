import sounddevice as sd
import soundfile as sf
import time
import threading
# 读取音频文件
data, fs = sf.read('./assets/jntm.mp3', dtype='float32')

# 播放音频
#sd.play(data, fs)

# default
# start_sample = int(5 * fs)  # 从第5秒开始播放
# end_sample = int(7.3 * fs)   # 播放到第10秒结束

# 播放音频的部分片段
# while True:
#     sd.play(data[start_sample:end_sample], fs)
#     sd.sleep(1000)
#     sd.play(data[start_sample:end_sample], fs)
#     sd.sleep(1000)
def play_audio_segment(data, fs, start_sample=int(5 * fs), end_sample=int(7.3 * fs)):
    sd.play(data[start_sample:end_sample], fs)

        #sd.wait()  # 等待音频播放完成
    sd.sleep(1000)  # 播放后暂停1秒
    #sd.wait()

# 创建并启动播放线程



# 逻辑有点烂，kunkun勿喷
# setup/common
try:
    def ikun_music_really_run(ikun_music_play_mode="common"):
        n=100
        if ikun_music_play_mode == "common":
            while n>0:
                n-=1
                time.sleep(0.3)
                while True:
                    playback_thread_one = threading.Thread(target=play_audio_segment, args=(data, fs,))
                    playback_thread_two = threading.Thread(target=play_audio_segment, args=(data, fs,))
                    playback_thread_one.start()
                    time.sleep(0.7)
                    playback_thread_two.start()
        else:
            while n>0:
                n-=1
                time.sleep(0.3)
                
                playback_thread_one = threading.Thread(target=play_audio_segment, args=(data, fs,))
                playback_thread_two = threading.Thread(target=play_audio_segment, args=(data, fs, ))
                playback_thread_one.start()
                time.sleep(0.7)
                playback_thread_two.start()
          
except KeyboardInterrupt:
    print("\n播放已停止")
    sd.stop()

if __name__=='__main__':
    ikun_music_really_run()