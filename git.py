import requests, os
from bs4 import BeautifulSoup
from tqdm import tqdm
'''
各个文件的作用
log.txt                 视频文件下载成功的链接
log_false.txt           视频文件下载失败的链接
err.txt                 不合格链接以及未完成下载的链接
使用说明：
输入文件为一个存储了i站视频链接的文本文件，编码为utf-8
视频链接是1行一个链接，会连续下载，可在运行界面查看下载进度
如果当中停止了，但是视频或者链接并没有下载完，再次载入是会检测已完成链接自动跳过
'''
url_file = input("把链接文件拖到此处")           #获取目标文本文件
if len(url_file) < 4 :
    print('文件输入错误')
    exit(0)
workfolder = os.getcwd()
try:
	os.mkdir('video')
except:
	print('找到video目录')
video_folder = workfolder + '\\video'
url_list = open(url_file,'r')       #读取链接文件，在下载程序结束前，文件一直被占用或者处于被读取状态
url_lists = url_list.readlines()        #读取链接列表

headers = {
    'user-agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 OPR/81.0.4196.52 (Edition GX-CN)'
}

def downloadbild(url: str, fname: str, real:str): 
    logfile = open('./log.txt', 'a+')
    logfile_flase = open('./log_false.txt','a+')
    logfile.seek(0)
    logfile_flase.seek(0)
    finshfiles = logfile.readlines()
    falsefiles = logfile_flase.readlines()
    if (real+'\n') in finshfiles :
        print('文件已下载过，将自动跳过')
        return True
    elif download(url, fname, real):
        if (real+'\n') in falsefiles :
            pass
        else:
            fname = fname[:-4]
            logfile_flase.seek(0,2)
            logfile_flase.write(fname+'\n')
            logfile_flase.write(real+'\n')
    else:
        try:
            fname = fname[:-4]
            logfile.write(fname+'\n')
            logfile.write(real+'\n')
            del logfile_flase[falsefiles.Index('\n'+fname)]
            del logfile_flase[falsefiles.Index('\n'+real)]
        except:
            pass
    logfile.close()
    logfile_flase.close()

def download(url: str, fname: str, real:str):
    try:
        os.chdir(video_folder)
    except:
        print('video文件夹无法进入或不存在，已下载到工作根目录')
    resp = requests.get(url, headers = headers, stream=True)
    size = 0
    total = int(resp.headers.get('content-length', 0))
    with open(fname, 'wb') as file, tqdm(
        desc=fname,
        total=total,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)
    if size != total :
        errurl(real,'下载未完成')
    os.chdir(workfolder)

def getfilename(url:str):
    try:
        res = requests.get(url, headers = headers, timeout=(3,7))
    except:
        return False
    soup = BeautifulSoup(res.text, 'html.parser')
    title_temp = soup.find('h1',class_='title')
    title = title_temp.text+'.mp4'
    title = rebuildname(title)
    print("文件名" + title)
    return title

def getdownurl(url:str):
    video_url = 'https://ecchi.iwara.tv/api/video' + url[29:]
    print(video_url)
    video_res = requests.get(video_url, headers=headers)
    video_json = video_res.json()
    dl_uri = video_json[0]['uri']
    return dl_uri

def errurl(url:str,note:str):
    logerr = open('./err.txt', 'a+')
    logerr.write(note + url+'\n')
    logerr.close()

def networktest():
    try:
        requests.get('https://ecchi.iwara.tv',timeout=(3,7))
    except:
        print('网络不行')
        exit(0)
networktest()

def rebuildname(name:str):
    rep = '-'
    for x in range(len(name)) :
        name = name.replace('|',rep)
        name = name.replace('\\',rep)
        name = name.replace(':',rep)
        name = name.replace('<',rep)
        name = name.replace('>',rep)
        name = name.replace('/',rep)
        name = name.replace('?',rep)
        name = name.replace('*',rep)
        name = name.replace('\"',rep)
    return name

for x in range(len(url_lists)):
    real_url = url_lists[x][:-1]
    print(f'第 {x+1} 个，共{len(url_lists)}个链接')
    if len(real_url) in range(16,17):
        real_url = 'https://ecchi.iwara.tv/videos/' + real_url
    elif len(real_url) < 16 :
        print("链接无效")
        continue
    print("当前链接为：\t"+real_url)
    try:
        filename = getfilename(real_url)
        downurl = 'https:'+getdownurl(real_url)
    except:
        print("\n链接连接失败，请检查网络或链接\n")
        errurl(real_url,'fin')
        continue
    print(downurl)
    downloadbild(downurl, filename, real_url)
url_list.close()