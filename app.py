import re
import os

import requests
import pywebio as io
out = io.output
ioin = io.input
pin = io.pin
import core

#校验输入是否正确
def check_input_url(url):
    #判断输入url类型
    if "BV" in url:
        video_info = re.findall('BV(..........)',url)[0]
        return
    elif "av" in url:
        video_info = re.findall('av(\d*)',url)[0]
        return
    elif "b23.tv" in url:
        url = re.findall('(https://b23.tv/.......)',url)[0]
        video_info = requests.get(url,allow_redirects=False).text#转换为网页版链接
        check_input_url(video_info)#重新检查
    elif "ep" in url:
        video_info = re.findall('ep(\d*)',url)[0]
        return
    elif "ss" in url:
        video_info = re.findall('ss(\d*)',url)[0]
        return
    elif "media/md" in url:#https://www.bilibili.com/bangumi/media/md28234644
        video_info = re.findall('md(\d*)',url)[0]
        return
    elif "space.bilibili.com" in url:#https://space.bilibili.com/1118188465
        video_info = re.findall('space.bilibili.com/(\d*)',url)[0]
        return
    #收藏夹处理
    elif "favlist?fid=" in url:#https://space.bilibili.com/1118188465/favlist?fid=1228786865
        video_info = re.findall('fid=(\d*)',url)[0]
        return
    #up主合集处理
    elif "?sid=" in url:#https://space.bilibili.com/1118188465/channel/collectiondetail?sid=28413
        video_info = re.findall('?sid=(\d*)',url)[0]
        return
    return '链接无效'

#获取被勾选视频数据
def get_video_list_info(num:int) -> list:
    """
    获取被勾选的视频数据
    """
    info_list = []
    for checkbox_one in range(1,num):
        if len(pin.pin['check_'+str(checkbox_one)]) != 0:
            info_list.append(pin.pin['check_'+str(checkbox_one)])
    return info_list

#获取选择的清晰度
def get_choice_quality() -> dict:
    """
    获取选择的视频清晰度
    """
    return_dict = {}
    return_dict['video'] = pin.pin['select_video']
    return_dict['audio'] = pin.pin['select_audio']
    return return_dict

#创建清晰度列表
def get_video_quality_list(data:dict) -> list:
    """
    返回[视频清晰度,音频清晰度]
    """
    out_audio_list = []
    out_video_list = []
    out_audio_list.append({'label':'默认最高音质','value':{'quality':30280}})#默认选中
    out_video_list.append({'label':'默认最高画质','value':{'quality':1000}})#默认选中
    for type in ['WEB','TV','APP']:#遍历不同接口
        for one_info in data['audio'][type]:#处理返回数据
            label = type+' '+one_info['quality_str']+' - ['+one_info['codec']+']   '+one_info['stream_size']#选项标签
            value = one_info#选项值
            return_dict = {'label':label,'value':value}
            out_audio_list.append(return_dict)
        for one_info in data['video'][type]:#处理返回数据
            label = type+' '+one_info['quality_str']+' - ['+one_info['codec']+']   '+one_info['stream_size']#选项标签
            value = one_info#选项值
            return_dict = {'label':label,'value':value}
            out_video_list.append(return_dict)
    return [out_video_list,out_audio_list]

#检查输入链接类型
def get_video_id(url) -> list:
    """
    检查输入链接类型
    输出为list [序号:int,id:str]
    """
    #判断输入url类型
    #BV解析
    if "BV" in url:
        video_info = re.findall('BV(..........)',url)[0]
        return [2,video_info]
    #AV解析
    elif "av" in url:
        video_info = re.findall('av(\d*)',url)[0]
        return [1,video_info]
    #手机端链接处理
    elif "b23.tv" in url:
        url = re.findall('(https://b23.tv/.......)',url)[0]
        video_info = requests.get(url,allow_redirects=False).text#转换为网页版链接
        get_video_id(video_info)#重新检查
    #ep类型处理
    elif "ep" in url:
        video_info = re.findall('ep(\d*)',url)[0]
        return [3,video_info]
    #ss类型处理
    elif "ss" in url:
        video_info = re.findall('ss(\d*)',url)[0]
        return [4,video_info]
    #media类型处理
    elif "media/md" in url:#https://www.bilibili.com/bangumi/media/md28234644
        video_info = re.findall('md(\d*)',url)[0]
        return [5,video_info]
    #up主投稿处理
    elif "space.bilibili.com" in url:#https://space.bilibili.com/1118188465
        video_info = re.findall('space.bilibili.com/(\d*)',url)[0]
        return [6,video_info]
    #收藏夹处理
    elif "favlist?fid=" in url:#https://space.bilibili.com/1118188465/favlist?fid=1228786865
        video_info = re.findall('fid=(\d*)',url)[0]
        return [7,video_info]
    #up主合集处理
    elif "?sid=" in url:#https://space.bilibili.com/1118188465/channel/collectiondetail?sid=28413
        video_info = re.findall('?sid=(\d*)',url)[0]
        return [7,video_info]
    return ''

#显示视频下载界面
def print_video_info(info):
    with out.use_scope('video_info'):#进入视频信息域
        data = info['data']
        with out.use_scope('up_info'):#切换到up信息域
            face = requests.get(data['up_face']).content#缓存图片
            out.put_row([out.put_image(face,height='50px'),out.put_text(data['up_name'])])#限制up头像大小
        out.put_text(data['video_title'])#视频标题
        cover = requests.get(data['video_cover']).content#缓存图片
        out.put_image(cover)#视频封面
        out.put_text(data['video_desc'])#视频简介
        out.put_text('视频类型 '+str(data['sort'])+'-'+str(data['sub_sort']))
        out.put_text('视频发布时间 '+data['bili_pubdate_str'])
        #out.put_column([info_title,info_cover,info_desc,info_sort])#设置为垂直排布

        #创建清晰度选择
        get_video_quality_info = get_video_quality_list(core.quality(data['list'][0]['page_av'],data['list'][0]['page_cid']))#读取视频列表第一个的清晰度
        with out.use_scope('quality'):#创建清晰度选择域
            pin.put_select(name='select_video',options=get_video_quality_info[0],value={'quality':1000})#创建视频选择
            pin.put_select(name='select_audio',options=get_video_quality_info[1],value={'quality':30280})#创建音频选择

        #创建列表
        table_list = []
        num = 0
        table_list.append(['选择','标题'])
        for one in data['list']:#遍历列表
            num += 1
            list_one = []
            list_one.append(pin.put_checkbox(name='check_'+str(num),options=[{'label':str(num),'value':one}]))#创建单选框
            list_one.append(one['page_name'])#标题
            table_list.append(list_one)
        out.put_table(table_list,position=-1)
        
        ioin.actions(buttons=[{'label':'开始下载','value':''}])#创建按键
        need_video_list:list = get_video_list_info(num)#获取被勾选的视频列表
        need_quality:dict = get_choice_quality()#获取选择的清晰度
        input()

def main():#主函数
    with out.use_scope('main'):#创建并进入main域
        url = io.input.input('请输入链接',type='url',validate=check_input_url)#限制类型为url,使用check_input_url检查内容
        #解析url
        out_url = get_video_id(url)
        get_video_info = core.info(out_url[0],out_url[1])
        print_video_info(get_video_info)#显示视频信息
        #io.input.actions('开始解析',buttons={})

#启动服务器
io.start_server(main,port=8080, debug=True)