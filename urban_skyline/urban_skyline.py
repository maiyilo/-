import random
import json
import os
import re
from scipy.interpolate import interp1d
from lxml import etree
from selenium import webdriver
import cv2
import numpy as np
from scipy import stats
import math
from heapq import nsmallest
import time
import copy

# edge驱动器位置
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedgedriver.exe"

# 导入archi svg的外接矩形参数
form_svg_path = r"D:\生成艺术\urban_skyline"

# 嵌套的archi svg最小外接矩形位置参数
# with open(form_svg_path +'\\form_archi\\'+ "write_json.json", encoding="utf-8") as f:
#     archi_viewBoxs = json.load(f)
archi_viewBoxs = {}

# 加载桥的缺口参数
# with open(form_svg_path +'\\form_archi\\'+ "bridge.json", encoding="utf-8") as f:
#     bridge_args = json.load(f)
bridge_args = {}
# 获取时间
input_time = time.strftime('%Y.%m.%d',time.localtime(time.time()))

# 团队图标的svg路径
icon_path = "archi/GDS+UR.svg"

# 用户选择的素材名字
archi_path = "archi"
archi_paths = []
for i in range(len(archi_paths)):
    archi_paths[i] = archi_path +"/"+ archi_paths[i]

# 内置的所有素材名字  tall_building库内不足八个，所以重复使用一个
tall_building = ['sketch_archi_014','sketch_archi_017','sketch_archi_018','sketch_archi_013','sketch_archi_003','sketch_archi_004','sketch_archi_005','sketch_archi_006']
lowrise = ['sketch_archi_016','sketch_archi_007']
bridge = ['sketch_archi_015']
plane = ['sketch_archi_001','sketch_archi_002']
boat = ['sketch_archi_008','sketch_archi_009']
mountain = ['sketch_archi_019']
cloud = ['sketch_archi_010','sketch_archi_011','sketch_archi_012']
plant = ['sketch_archi_022','sketch_archi_023']
pedestrian = ['sketch_archi_020','sketch_archi_021']


# 地平线线宽
hori_wid = 4

# 画布  可能需要更改，提高泛化性
w = 800
h = 500

city_colors = ["#0B0B0B",'#EA1DBA','#64F6F6','#FE9239','#27A463']
city_colors = ['#0B0B0B','#F5649B','#3EE91D','#3CF0FE','#A4259A']
city_colors = ['#0B0B0B','#BE14E9','#64F6B8','#FE433C','#77C57A']
city_colors = ['#0B0B0B','#64B5F6','#EA1D60','#FEEA3D','#25A499']
n = len(city_colors)

background = 'white'

# 柏林噪声参数
fineness = 1/10
persistence = 1/2

# 定义解析器
parser = etree.XMLParser(encoding = "utf-8")

# 如果用户选的太少，保证archi多样性会自动推荐一些archi
def recommend(archi_paths):
    '''
    :param archi_paths: 用户的输入archi名字
    :return: 需要用来作画的建筑列表，山脉曲线archi列表，云彩列表，植被列表，船列表，行人列表
    '''

    # 补充山脉至1种以上，云彩1种以上，草丛3种以上，高楼4种以上，矮楼4种以上，桥梁1种以上，飞机1种以上，船1种以上，行人2种以上
    tall_num = 0
    low_num = 0
    bri_num = 0
    air_num = 0
    boat_num = 0

    # 返回的参数列表
    building = []
    mou = []
    clo = []
    pla = []
    boa = []
    ped = []

    mountain_copy = mountain[:]
    cloud_copy = cloud[:]
    plant_copy = plant[:]
    tall_building_copy = tall_building[:]
    lowrise_copy = lowrise[:]
    bridge_copy = bridge[:]
    plane_copy = plane[:]
    boat_copy = boat[:]
    pedestrian_copy = pedestrian[:]

    # 统计用户的archi种类
    for archi in archi_paths:
        name = archi.split("/")[-1].split(".")[0]
        if name in mountain:
            mou.append(archi_path+'/'+name+'.svg')
            mountain_copy.remove(name)
        elif name in cloud:
            clo.append(archi_path+'/'+name+'.svg')
            cloud_copy.remove(name)
        elif name in plant:
            pla.append(archi_path+'/'+name+'.svg')
            plant_copy.remove(name)
        elif name in pedestrian:
            ped.append(archi_path + '/' + name + '.svg')
            pedestrian_copy.remove(name)
        elif name in tall_building:
            tall_num += 1
            building.append(archi_path+'/'+name+'.svg')
            tall_building_copy.remove(name)
        elif name in lowrise:
            low_num += 1
            building.append(archi_path + '/' + name + '.svg')
            lowrise_copy.remove(name)
        elif name in bridge:
            bri_num += 1
            building.append(archi_path + '/' + name + '.svg')
            bridge_copy.remove(name)
        elif name in plane:
            air_num += 1
            building.append(archi_path + '/' + name + '.svg')
            plane_copy.remove(name)
        elif name in boat:
            boat_num += 1
            boa.append(archi_path + '/' + name + '.svg')
            boat_copy.remove(name)
    # 补充各种种类
    if len(mou) < 1:
        mou.append(archi_path + '/' + random.choice(mountain_copy) + '.svg')
    if len(clo) < 1:
        clo.append(archi_path + '/' + random.choice(cloud_copy) + '.svg')
    while len(pla) < 2:
        name = random.choice(plant_copy)
        pla.append(archi_path + '/' + name + '.svg')
        plant_copy.remove(name)
    while len(ped) < 2:
        name = random.choice(pedestrian_copy)
        ped.append(archi_path + '/' + name + '.svg')
        pedestrian_copy.remove(name)

    # 打乱用户的选择
    random.shuffle(building)
    recom = []
    while tall_num < 8:
        name = random.choice(tall_building_copy)
        recom.append(archi_path + '/' + name + '.svg')
        tall_building_copy.remove(name)
        tall_num += 1
    while low_num < 1:
        name = random.choice(lowrise_copy)
        recom.append(archi_path + '/' + name + '.svg')
        lowrise_copy.remove(name)
        low_num += 1
    while bri_num < 1:
        name = random.choice(bridge_copy)
        recom.append(archi_path + '/' + name + '.svg')
        bridge_copy.remove(name)
        bri_num += 1
    while air_num < 1:
        name = random.choice(plane_copy)
        recom.append(archi_path + '/' + name + '.svg')
        plane_copy.remove(name)
        air_num += 1
    while boat_num < 1:
        name = random.choice(boat_copy)
        boa.append(archi_path + '/' + name + '.svg')
        boat_copy.remove(name)
        boat_num += 1
    random.shuffle(recom)
    building.extend(recom)
    return building,mou,clo,pla,boa,ped


def def_css(colors):
    '''
    colors:配色列表
    输出为svg内嵌式css代码
    '''

    css_data = '<style xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" type="text/css">'

    # 定义颜色样式
    for i in range(len(colors) + 10):
        if i == len(colors) + 3:  # 为云彩样式
            # 注意为了实现遮挡，fill不能为none，而为背景色
            css_data += f'use.st-{i}' + '{ stroke:red'  + f'; fill:{"#DCEDF5"}' + f';fill-opacity:{0.5}' + ' }\n'
        elif i < len(colors) - 1:
            css_data += f'use.st-{i}'+ '{ stroke:'+ f'{colors[i]}'+f'; fill:{"none"}'+f';stroke-width:{1}'+' }\n'
        elif i == len(colors) - 1:
            css_data += f'use.st-{i}' + '{ stroke:' + f'{colors[i]}' + f'; fill:{background}' + f';stroke-width:{10}' + ' }\n'
        # 山脉的线宽和其他建筑不一样，额外定义样式
        elif i < len(colors) + 3:
            css_data += f'use.st-{i}' + '{ stroke:' + f'{colors[i-len(colors)]}' + f'; fill:{"none"}' + f';stroke-width:{10}' + ' }\n'

        elif i < len(colors) + 7:
            # 小船需要遮挡地平线
            css_data += f'use.st-{i}' + '{ stroke:' + f'{colors[i-len(colors)-4]}' + f'; fill:{background}' + f';stroke-width:{1}' + ' }\n'
        else:
            # 行人css
            css_data += f'use.st-{i}' + '{ stroke:' + f'{colors[i - len(colors) - 7]}' + f'; fill:{background}' + f';stroke-width:{10}' + ' }\n'


    css_data += '</style>'

    return css_data

# 根据archi路径导入到<defs>中
def def_archi(building,mou,clo,pla,boa,ped,icon_path):
    '''
    :param building: 建筑类archi的路径列表
    :param mou: 山脉路径列表
    :param clo: 云彩路径列表
    :param pla: 植物路径列表
    :param boa: 小船路径列表
    :param ped: 行人路径列表
    :param icon_path: 团队图标路径
    :return: 返回提取的archi svg代码  <defs></defs>
    '''
    paths = []
    paths.extend(building)
    paths.extend(mou)
    paths.extend(clo)
    paths.extend(pla)
    paths.extend(boa)
    paths.extend(ped)
    archi_data = "<defs>\n"
    for i in range(len(paths)):
        # 传入两个参数，第一个参数是文件名，第二个参数是解析器。
        tree = etree.parse(paths[i], parser=parser)  # 查看解析出的tree的内容
        svg_text = etree.tostring(tree, encoding='utf-8').decode('utf-8')
        svg_root = etree.XML(svg_text)
        root = etree.HTML(svg_text)

        name = paths[i].split("/")[-1].split(".")[0]
        rect_arg = root.xpath('//archi/boundingrect/ele/text()')[0].split(',')
        for j in range(len(rect_arg)):
            rect_arg[j] = float(rect_arg[j])
        archi_viewBoxs[name] = rect_arg

        if name in bridge:
            gap_arg = root.xpath('//archi/gap/ele/text()')[0].split(',')
            for j in range(len(gap_arg)):
                gap_arg[j] = float(gap_arg[j])
            bridge_args[name] = gap_arg

        archi_data += f"<g id=\'archi_{name}\'>\n"
        # archi_data += f'<rect width="100%" height="100%" stroke="#000" stroke-width="10" fill="#f40" />'
        for child in svg_root:
            if child.tag.split('}')[-1] != "style":
                data = etree.tostring(child, encoding="utf-8").decode('utf-8') + "\n"

                # 通过正则表达式过滤fill stroke属性
                data = re.sub('stroke:.*?;', '', data)
                data = re.sub('stroke-width:.*?;','',data)
                data = re.sub('fill:.*?;', '', data)
                data = re.sub('stroke=".*?"', '', data)
                data = re.sub('stroke-width=".*?"', '', data)
                archi_data += re.sub('fill=".*?"', '', data)
        archi_data += "</g>\n"

    # 团队图标需要保留样式与颜色
    tree = etree.parse(icon_path, parser=parser)  # 查看解析出的tree的内容
    svg_text = etree.tostring(tree, encoding='utf-8').decode('utf-8')
    svg_root = etree.XML(svg_text)
    root = etree.HTML(svg_text)

    name = icon_path.split("/")[-1].split(".")[0]
    rect_arg = root.xpath('//archi/boundingrect/ele/text()')[0].split(',')
    for j in range(len(rect_arg)):
        rect_arg[j] = float(rect_arg[j])
    archi_viewBoxs[name] = rect_arg

    archi_data += f"<g id=\'archi_{name}\'>\n"
    # archi_data += f'<rect width="100%" height="100%" stroke="#000" stroke-width="10" fill="#f40" />'
    for child in svg_root:
        data = etree.tostring(child, encoding="utf-8").decode('utf-8') + "\n"
        archi_data += data
    archi_data += "</g>\n"

    archi_data += "</defs>\n"
    return archi_data


# 三次差值
def cubic_interpolate(start,end,input_x, input_y, fineness):
    '''
    :param start: 柏林噪声x开始位置
    :param end: 柏林噪声x结束位置
    :param input_x: 传入采样点
    :param input_y: 传入采样点
    :param fineness: 划分区间
    :return: 返回插值坐标列表
    '''
    x = []
    y = []
    cubic_func = interp1d(input_x, input_y, kind = 'cubic')
    num = int((end - start)/ fineness)
    for inter_x in list(np.linspace(start, end, num)):
        inter_y = cubic_func(inter_x)
        x.append(inter_x)
        y.append(inter_y)
    return x, y

# 一维柏林噪声
def perlin(start,end,upbound,downbound,i):
    '''
    :param end: x的开始
    :param start: x的结束
    :param upbound: y的上界
    :param downbound: y的下界
    :param i: i可以为负数，i越小，波长越大，导致采样点变少，少于四个点会不足以三次差值
    :return: 一系列平滑柏林噪声x，y坐标点
    '''

    amplitude = persistence ** i
    frequent = 2 ** i
    wavelength = 1 / frequent

    num = int((end - start) / wavelength + 1)
    x = np.linspace(start, end, num)
    if len(x) > 3:
        # 三次插值需要至少四个点
        y = []
        for index, data in enumerate(x):
            noise_y = random.uniform(downbound, upbound)
            y.append(noise_y)
        cubic_x, cubic_y = cubic_interpolate(start, end, x, y, fineness)
        return cubic_x,cubic_y
    else:
        return [],[]

# 画中景的连绵城市边际线
def draw_mid_shot(upbound,downbound,color,stroke_wid):
    '''
    :param upbound: 边际线上边界位置
    :param downbound: 边际线下边界位置
    :param color: 边缘的颜色
    :param stroke_wid: 画笔粗细
    :return: 画边际线的svg代码
    '''

    # 生成绘制path的控制点,从左边(x=0.1*h)开始生成
    x = 0.05 * h
    y0 = downbound
    mid_shot = f'<path id="mid shot" d="M {x} {y0} '
    while x < w - 0.05 * h:

        if random.random() < 0.1: # 随机加入随机的抖动(4个点)
            # 柏林噪声
            wid = random.uniform(20,40)
            x_list,y_list = perlin(x,x+wid if x+wid < w - 0.05*h else w-0.05*h,upbound,downbound,-2.5)
            if x_list != []:
                for i in range(len(x_list)):
                    mid_shot += f'L {x_list[i]} {y_list[i]}'
                y = y_list[-1]
                x += wid
        else: # 随机取y
            y = random.uniform(upbound, downbound)
            mid_shot += f"L {x} {y} "
            if y < y0:  # 城市线，宽度稍微长一点
                wid = random.uniform(18, 30)
            else:
                wid = random.uniform(0, 12)
        x += wid
        # 放置越界
        x = x if x < w - 0.05 * h else w - 0.05 * h
        y0 = y
        mid_shot += f"L {x} {y0} "

    mid_shot += f'" ' \
                f'stroke-linejoin="round" stroke="{color}" fill="none" stroke-width="{stroke_wid}"/>\n'

    return mid_shot


# 利用柏林噪声画云彩
def draw_cloud(upbound,downbound,color):
    '''
    :param upbound: 边际线上边界位置
    :param downbound: 边际线下边界位置
    :param color: 填充的颜色
    :param stroke_wid: 画笔粗细
    :return: 画云朵的svg代码
    '''

    # 调用云彩svg
    name = random.choice(clo)
    name = name.split('/')[-1].split('.')[0]
    # 通过name寻找到svg的外接矩形参数
    rect_arg = archi_viewBoxs[name]

    # 无视原图比例平铺
    cloud_data = f'<svg id="{name}" x="{0.05 * h}" y="{upbound}" width="{w - 0.1 * h}" height="{downbound - upbound}" viewBox="' \
                    f'{rect_arg[0]} {rect_arg[1]} {rect_arg[2]} {rect_arg[3]}" onclick="printInfo(this)" preserveAspectRatio="none" xml:space="preserve">\n'

    cloud_data += f'<use class="st-{n-1}" xlink:href="#archi_{name}"/>'
    cloud_data += "</svg>\n"

    return cloud_data

    # x_list,y_list = perlin(0.1*w,0.9*w,upbound,upbound+(downbound-upbound)/2,-6)
    # down_x,down_y = perlin(0.1*w,0.9*w,upbound+(downbound-upbound)/2,downbound,-6)
    # down_x.reverse()
    # down_y.reverse()
    # x_list.extend(down_x)
    # y_list.extend(down_y)
    #
    # if len(x_list) > 0:
    #     cloud = f'<path id="cloud" d="M {x_list[0]} {y_list[0]}'
    #     for i in range(1,len(x_list)):
    #         cloud += f"L {x_list[i]} {y_list[i]} "
    #     cloud += f'z" ' \
    #                 f' stroke="none" fill="{color}" opacity="0.5"/>\n'
    #     return cloud
    # else:
    #     return ""

# 画山脉
def draw_mountain(upbound,downbound,mou):
    '''
    :param upbound: 边际线上边界位置
    :param downbound: 边际线下边界位置
    :param mou: 填充的颜色
    :return: 画山脉的svg代码
    '''

    # #柏林噪声模拟山脉
    # x_list,y_list = perlin(0.1*w,0.9*w,upbound,downbound,-7)
    #
    # if len(x_list) > 0:
    #     mountain = f'<polyline id="mountain" points="{x_list[0]},{y_list[0]}'
    #     for i in range(1,len(x_list)):
    #         mountain += f" {x_list[i]},{y_list[i]} "
    #     mountain += f' " stroke="{color}" fill="none" />\n'
    #     return mountain
    # else:
    #     return ""

    # 随机选取mountain中的一个作为山脉
    name = random.choice(mou)
    name = name.split('/')[-1].split('.')[0]
    # 通过name寻找到svg的外接矩形参数
    rect_arg = archi_viewBoxs[name]

    # 无视原图比例平铺
    mountain_data = f'<svg id="{name}" x="{0.05*h}" y="{upbound}" width="{w - 0.1 * h}" height="{downbound-upbound}" viewBox="' \
               f'{rect_arg[0]} {rect_arg[1]} {rect_arg[2]} {rect_arg[3]}" onclick="printInfo(this)" preserveAspectRatio="none" xml:space="preserve">\n'

    k = int(len(city_colors)+random.uniform(0,3))
    mountain_data += f'<use class="st-{k}" xlink:href="#archi_{name}"/>'

    mountain_data += "</svg>\n"

    return mountain_data
# 随机画地平线
def draw_horizon(upbound,downbound,color,stroke_wid):
    '''
    :param upbound: 地平线位置上界
    :param downbound: 地平线位置下界
    :color: 线条颜色
    :stroke_wid: 线条宽度
    :return: 画地平线的代码，和地平线选择的y坐标位置
    '''
    y = random.uniform(upbound,downbound)
    horizon = f'<line x1="{0.05*h}" y1="{y}" x2="{w - 0.05*h}" y2="{y}" stroke="{color}" stroke-width="{stroke_wid}" />\n'
    return horizon,y

# 调用archi的代码
def use_archi(name,x,y,wid,hei,k):
    '''
    :param name: 选择的archi名字（暂定为svg文件名字）
    :param x: 平移的参数
    :param y: 平移的参数
    :param wid: 为archi的长
    :param hei: 为archi的宽
    :param k: 使用的css样式
    :return: 返回调用archi代码的svg代码
    '''

    # 通过name寻找到svg的外接矩形参数
    rect_arg = archi_viewBoxs[name]

    # preserveAspectRatio="xMidYMid none" 不保持宽高
    # 每个archi的view需要通过javascript解析得到
    # x = x + random.uniform(-4,4)
    use_data = f'<svg id="{name}" x="{x}" y="{y}" width="{wid}" height="{hei}" viewBox="' \
               f'{rect_arg[0]} {rect_arg[1]} {rect_arg[2]} {rect_arg[3]}" onclick="printInfo(this)" preserveAspectRatio="xMidYMax meet" xml:space="preserve">\n'

    use_data += f'<use class="st-{k}" xlink:href="#archi_{name}"/>'

    use_data += "</svg>\n"

    return use_data

# 前景的排列趋势，高斯密度分布、马鞍形
def foreground(downbound):
    '''
    :param downbound: 地平线位置
    :param stroke_wid: 画笔粗细
    :return: 前景的绘画svg代码,缺口位置列表
    '''


    foreground_data = ""
    boat_data = ""
    gap_location = []

    # 建筑位置与对应样式
    archi_occupy = []
    building_class = []


    # 只放置船和飞机各一个
    plane_num = 1

    # 随机设置最高建筑的屋顶位置，最高建筑暂定为普通建筑，非船，非桥
    upbound = random.uniform(0.05*h+(0.8*h)*0.15,0.05*h+(0.8*h)*0.25)

    # 采样点
    x_list = list(np.linspace(0.05*h,w-0.05*h,1000))

    # 正态分布的极值位置的x坐标
    mu = random.uniform(0.05*h+(w-0.1*h)*0.3,0.05*h+(w-0.1*h)*0.8)
    sd = 350

    # 计算合适的放大比例
    k = (downbound-upbound)*math.sqrt(2*math.pi)*sd
    # 生成数据点
    y_list = downbound-k*stats.norm(mu, sd).pdf(x_list)

    # y_list缩放到画中合适位置
    bound = random.uniform(0.05*h+(0.8*h)*0.45,0.05*h+(0.8*h)*0.55)
    maxy = max(y_list)
    for i in range(len(y_list)):
        y_list[i] = (y_list[i]-upbound)/(maxy-upbound)*(bound-upbound)+upbound
    archi_heights = list(downbound-y_list)

    maxy = max(y_list)
    miny = min(y_list)
    y_list = list(y_list)
    max_index = y_list.index(maxy)
    min_index = y_list.index(miny)
    mid_index = int((max_index+min_index)/2)

    # 向左边开始摆放archi
    x = x_list[2]

    paths = archi_paths
    paths.reverse()
    while x <= w - 0.05*h and len(paths) != 0:

        archi = paths.pop()
        name = archi.split("/")[-1].split(".")[0]
        rect_arg = archi_viewBoxs[name]

        # 按建筑类型设计放缩方式
        if name in lowrise:
            archi_wid = random.uniform((w - 0.1*h) * 0.1, (w-0.1*h) * 0.2)
            archi_hei = rect_arg[3] / rect_arg[2] * archi_wid
            if x + archi_wid > w - 0.05*h:
                # 超出右边界
                break
            else:
                archi_occupy.append([x, x + archi_wid])
                # building取配色中的前三种随机上色
                k = int(random.uniform(0, 3))
                building_class.append(k+12)
                foreground_data += use_archi(name, x, downbound - archi_hei, archi_wid, archi_hei,k)

            x += archi_wid + random.uniform(8, 20)
        elif name in tall_building:
            # 高楼archi
            if random.random() > 0.2:
                # 根据x位置寻找合适的高度
                archi_hei = archi_heights[x_list.index(nsmallest(1, x_list, key=lambda s: abs(s - x))[0])]
            else:
                archi_hei = random.uniform(0.8 * h * 0.3, 0.8 * h * 0.4)
            archi_wid = rect_arg[2] / rect_arg[3] * archi_hei
            if archi_wid > (w-0.1*h)*0.1:
                # 高楼的宽度太大，不美观，需要限制
                archi_wid = random.uniform((w-0.1*h)*0.06,(w-0.1*h)*0.1)
                archi_hei = rect_arg[3] / rect_arg[2] * archi_wid
            if x + archi_wid > w-0.05*h:
                # 超出右边界,不放置
                break
            else:
                archi_occupy.append([x, x + archi_wid])
                k = int(random.uniform(0, 3))
                building_class.append(k+12)
                foreground_data += use_archi(name, x, downbound - archi_hei, archi_wid, archi_hei,k)
            x += archi_wid + random.uniform(8, 20)
        elif name in bridge:
            # archi为桥类型
            archi_wid = random.uniform((w-0.1*h) * 0.1, (w-0.1*h) * 0.2)
            # 缩放比例r
            r = archi_wid / rect_arg[2]
            archi_hei = rect_arg[3] * r
            if x + archi_wid > w - 0.05*h:
                # 超出右边界
                break
            else:
                archi_occupy.append([x, x + archi_wid])
                k = int(random.uniform(0, 3))
                building_class.append(k+12)
                foreground_data += use_archi(name, x, downbound - archi_hei, archi_wid, archi_hei,k)

                # archi外接矩形在x~x+archi_wid之间，由此计算缺口位置
                x1 = bridge_args[name][0]
                x2 = bridge_args[name][1]

                left = (x1 - rect_arg[0]) * r
                line_wid = (x2 - x1) * r

                # 在画作中缺口实际位置
                x1 = x + left
                x2 = x1 + line_wid
                y = downbound

                gap_location.append((x1,y,x2,y))

            x += archi_wid + random.uniform(8, 20)
        elif name in plane and plane_num == 1:
            # 飞机类型
            archi_hei = random.uniform(0.8 * h * 0.05, 0.8 * h * 0.1)
            archi_wid = rect_arg[2] / rect_arg[3] * archi_hei

            k = int(random.uniform(9, 12))
            foreground_data += use_archi(name, x_list[mid_index], y_list[mid_index] - random.uniform((0.8*h)*0.1,(0.8*h)*0.2), archi_wid, archi_hei,k)
            plane_num -= 1
    # for i in range(len(x_list)):
    #     foreground_data += f'<circle cx="{x_list[i]}" cy="{y_list[i]}" r="2" />'


    return foreground_data,gap_location,archi_occupy,building_class

def draw_boat(gap_location,downbound,boa):
    '''
    :param gap_location: 地平线缺口列表
    :param downbound: 地平线缺口y位置
    :param boa: 作画的船archi路径列表
    :return: 画小船svg代码
    '''
    boat_data = ""
    name = random.choice(boa)
    name = name.split('/')[-1].split('.')[0]
    # 通过name寻找到svg的外接矩形参数
    rect_arg = archi_viewBoxs[name]

    if len(gap_location) == 0:
        left_x = 0
        right_x = 0
    else:
        left_x = gap_location[0][0] - (gap_location[0][2] - gap_location[0][0])
        right_x = gap_location[0][2] + (gap_location[0][2] - gap_location[0][0])

    d = 0.9 * h - downbound
    archi_hei = random.uniform(d / 2,2*d/3)
    archi_wid = rect_arg[2] / rect_arg[3] * archi_hei
    if archi_wid > 0.3 * (w - 0.1 * h):
        # 船太长了，需要限制
        archi_wid = random.uniform((w - 0.1 * h) * 0.2, (w - 0.1 * h) * 0.3)
        archi_hei = rect_arg[3] / rect_arg[2] * archi_wid

    pos_x = random.uniform(0.05 * h, w - 0.05 * h - (w - 0.1 * h) * 0.3)
    while ((pos_x > left_x and pos_x < right_x) or (pos_x + archi_wid > left_x and pos_x + archi_wid < right_x) or (
            left_x > pos_x and left_x < pos_x + archi_wid) or (right_x > pos_x and right_x < pos_x + archi_wid)):
        pos_x = random.uniform(0.05 * h, w - 0.05 * h - (w - 0.1 * h) * 0.3)

    pos_y = downbound - random.uniform(d / 6, d / 5)
    k = int(random.uniform(9, 12))
    boat_data += use_archi(name, pos_x, pos_y, archi_wid, archi_hei,k)

    perlin_x, perlin_y = perlin(pos_x, pos_x + archi_wid, pos_y + archi_hei + 0.015 * (0.8 * h),
                                pos_y + archi_hei + 0.025 * (0.8 * h), -3)

    if len(perlin_x) > 0:
        boat_data += f'<polyline id="wave" points="{perlin_x[0]},{perlin_y[0]}'
        for i in range(1, len(perlin_x)):
            boat_data += f" {perlin_x[i]},{perlin_y[i]} "
        boat_data += f' " stroke="blue" fill="none" />\n'
    return boat_data
# 画地平线缺口和缺口下的水波纹
def draw_gap_wave(gap_location,wave_color):
    '''
    :param gap_location: 缺口位置列表
    :param wave_color: 波浪颜色
    :return: 画缺口和水波纹的svg代码
    '''

    gap_wave_data = ''

    if len(gap_location) == 0:
        return ""
    for each in gap_location:
        x1 = each[0]
        y = each[1]
        x2 = each[2]

        # 用背景色画缺口
        gap_wave_data += f'<line id="gap" x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{background}" stroke-width="{hori_wid+1}"/>\n'

        # 画波纹
        gap_len = x2 - x1

        # 注意防止波浪超出画布
        x_list, y_list = perlin(max(x1 - gap_len, 0.05 * h), min(x2 + gap_len, w - 0.05*h), y + 0.015 * (0.8 * h),
                                y + 0.025 * (0.8 * h), -3)

        if len(x_list) > 0:
            gap_wave_data += f'<polyline id="wave" points="{x_list[0]},{y_list[0]}'
            for i in range(1, len(x_list)):
                gap_wave_data += f" {x_list[i]},{y_list[i]} "
            gap_wave_data += f' " stroke="{wave_color}" fill="none" />\n'

        # else:
        #     # 生成贝塞尔曲线控制点
        #     x_list = list(np.linspace(max(x1 - gap_len, 0.1 * w), min(x2 + gap_len, 0.9 * w),7))
        #     const_y = y + 0.02 * (0.8 * h)
        #     y_list = []
        #     print("haha")
        #     for i in range(7):
        #         if i%2 == 0:
        #             y_list.append(y + 0.01 * (0.8 * h))
        #         else:
        #             y_list.append(y + 0.03 * (0.8 * h))
        #     gap_wave_data += f'<path id="wave" d="M {x_list[0]},{const_y} C {x_list[0]},{y_list[0]} {x_list[1]},{y_list[1]} {x_list[1]},{const_y} '
        #     for i in range(2,7):
        #         gap_wave_data += f'S {x_list[i]},{y_list[i]} {x_list[i]},{const_y} '
        #     gap_wave_data += f'" stroke="{wave_color}" fill="none" />\n'
        return gap_wave_data



# 柏林噪声绘制草丛
def draw_plant(gap_location,upbound,pla,downbound,k=5):
    '''
    :param gap_location: 地平线缺口位置列表,例如[(x1,y,x2,y)]
    :param upbound: 草丛的上界区域
    :param pla: 作画用到的植被路径列表
    :param downbound: 地平线位置
    :param k: 需要生成的草丛个数
    :return: 绘制草丛的svg代码
    '''

    plant_data = ""
    i = 0

    # 拷贝一份，防止修改
    gaps = copy.deepcopy(gap_location)
    threshold = 6000
    count = 0
    while i < k and count < threshold:
        count += 1
        x1 = random.uniform(0.05*h,w - 0.05*h)
        plant_wid = random.uniform(0.1*(w-0.1*h),0.15*(w-0.1*h))
        x2 = min(w-0.1*h,x1+plant_wid)

        if x2 - x1 < (w - 0.1*h) * 0.1:
            # 草丛的跨度太小，舍去
            continue

        # 是否在x1~x2放置草丛
        lay = True
        if len(gaps) != 0:
            for each_gap in gaps:
                left_x = each_gap[0]
                right_x = each_gap[2]
                if (x1 > left_x and x1 < right_x) or (x2 > left_x and x2 < right_x) or (
                        left_x > x1 and left_x < x2) or (right_x > x1 and right_x < x2):
                    # x1~x2位置可能会与地平线缺口或者其他草丛产生交集
                    lay = False
                    break
        if lay:
            i += 1
            # 引用植物archi svg
            name = random.choice(pla).split('/')[-1].split('.')[0]
            # 通过name寻找到svg的外接矩形参数
            rect_arg = archi_viewBoxs[name]


            plant_data += f'<svg id="{name}" x="{x1}" y="{upbound}" width="{x2-x1}" height="{downbound - upbound}" viewBox="' \
                            f'{rect_arg[0]} {rect_arg[1]} {rect_arg[2]} {rect_arg[3]}" onclick="printInfo(this)" preserveAspectRatio="xMidYMid meet" xml:space="preserve">\n'

            plant_data += f'<use class="st-{4}" xlink:href="#archi_{name}"/>'

            plant_data += "</svg>\n"
            gaps.append([x1, downbound, x2, downbound])

    return plant_data
            # if random.random() < 0.5:
            #     # 柏林噪声生成草丛
            #     x_list, y_list = perlin(x1 + (0.8 * w) * 0.025, x2 - (0.8 * 2) * 0.025, upbound,
            #                             downbound - (0.8 * h) * 0.025, -3.8)
            #     if len(x_list) > 0:
            #         i += 1
            #         plant_data += f'<polyline id="wave" points="{x1},{downbound}'
            #         for j in range(len(x_list)):
            #             plant_data += f" {x_list[j]},{y_list[j]} "
            #         plant_data += f' {x2},{downbound} '
            #         plant_data += f' " stroke="{plant_color}" fill="{background}" />\n'
            #         gaps.append([x1, downbound, x2, downbound])
            #
            #
            # else:
            #     # 生成树
            #     i += 1
            #     plant_data += f'<g>\n'
            #     plant_data += f'<polyline points="{(x1+x2)/2},{downbound} {(x1+x2)/2},{downbound-(0.8*h)*0.03}" stroke="{plant_color}" />\n'
            #     plant_data += f'<circle cx="{(x1+x2)/2}" cy="{downbound-(0.8*h)*0.06}" r="{(0.8*h)*0.03}" stroke="{plant_color}" fill="{background}"/>'
            #     plant_data += '</g>'
            #     gaps.append([x1, downbound, x2, downbound])

# 柏林噪声绘制草丛
def draw_pedestrian(gap_location,archi_occupy,building_class,upbound,ped,downbound,k=3):
    '''
    :param gap_location: 地平线缺口位置列表,例如[(x1,y,x2,y)]
    :param archi_occupy: 建筑占据的位置
    :param building_class: 建筑对应的css样式
    :param upbound: 草丛的上界区域
    :param ped: 作画用到的植被路径列表
    :param downbound: 地平线位置
    :param k: 需要生成的草丛个数
    :return: 绘制草丛的svg代码
    '''

    pedestrian_data = ""
    i = 0

    # 拷贝一份，防止修改
    gaps = copy.deepcopy(gap_location)
    threshold = 6000
    count = 0
    while i < k and count < threshold:
        count += 1
        x1 = random.uniform(0.05*h,w - 0.05*h)
        pedestrian_wid = random.uniform(0.1*(w-0.1*h),0.15*(w-0.1*h))
        x2 = min(w-0.1*h,x1+pedestrian_wid)

        if x2 - x1 < (w - 0.1*h) * 0.1:
            # 草丛的跨度太小，舍去
            continue

        # 是否在x1~x2放置草丛
        lay = True
        if len(gaps) != 0:
            for each_gap in gaps:
                left_x = each_gap[0]
                right_x = each_gap[2]
                if (x1 > left_x and x1 < right_x) or (x2 > left_x and x2 < right_x) or (
                        left_x > x1 and left_x < x2) or (right_x > x1 and right_x < x2):
                    # x1~x2位置可能会与地平线缺口或者其他草丛产生交集
                    lay = False
                    break
        if lay:
            i += 1
            # 引用植物archi svg
            name = random.choice(ped).split('/')[-1].split('.')[0]
            # 通过name寻找到svg的外接矩形参数
            rect_arg = archi_viewBoxs[name]


            pedestrian_data += f'<svg id="{name}" x="{x1}" y="{upbound}" width="{x2-x1}" height="{downbound - upbound}" viewBox="' \
                            f'{rect_arg[0]} {rect_arg[1]} {rect_arg[2]} {rect_arg[3]}" onclick="printInfo(this)" preserveAspectRatio="xMidYMid meet" xml:space="preserve">\n'
            if len(archi_occupy) == 0:
                index = int(random.uniform(5, 8))
            else:
                cls_num = 0
                ped_cls = [12,13,14]
                for occ_i in range(len(archi_occupy)):
                    each_occupy = archi_occupy[occ_i]
                    left_x = each_occupy[0]
                    right_x = each_occupy[1]
                    if (x1 > left_x and x1 < right_x) or (x2 > left_x and x2 < right_x) or (
                            left_x > x1 and left_x < x2) or (right_x > x1 and right_x < x2):
                        if building_class[occ_i] in ped_cls:
                            ped_cls.remove(building_class[occ_i])
                        cls_num += 1
                        if cls_num == 2:
                            break
                index = random.choice(ped_cls)
            pedestrian_data += f'<use class="st-{index}" xlink:href="#archi_{name}"/>'

            pedestrian_data += "</svg>\n"
            gaps.append([x1, downbound, x2, downbound])

    return pedestrian_data

# 用户的签名与本团队的icon图标
def sign_icon(input_time,icon_path):
    '''
    :param input_time: 生成画作的时间
    :param icon_path: 团队图标的路径
    :return:
    '''
    outer_data = ""
    x = 0.05 * h
    y = 0.9 * h
    outer_data += f'<text x="{x}" y="{y}">{"轮廓风格示例"}</text>\n'
    outer_data += f'<text x="{x}" y="{y+0.05*h}">{input_time}</text>\n'

    # 贴上团队图标
    name = icon_path.split("/")[-1].split(".")[0]
    rect_arg = archi_viewBoxs[name]
    archi_hei = 0.1*h
    archi_wid = rect_arg[2] / rect_arg[3] * archi_hei

    rect_arg = archi_viewBoxs[name]
    outer_data += f'<svg id="{name}" x="{w - 0.05*h - archi_wid}" y="{h - 0.12*h}" width="{archi_wid}" height="{archi_hei}" viewBox="' \
               f'{rect_arg[0]} {rect_arg[1]} {rect_arg[2]} {rect_arg[3]}" onclick="printInfo(this)" preserveAspectRatio="xMidYMax meet" xml:space="preserve">\n'
    outer_data += f'<use xlink:href="#archi_{name}"/>'

    outer_data += "</svg>\n"
    return outer_data

def create_svg(name,css_data,archi_data):
    '''
    :param name: 要创建的svg文件路径名
    :param css_data: 样式代码字符串
    :param archi_data: 使用archi代码字符串
    :param svg_data:
    :param rect_args: 矩形参数列表
    :return: svg文件
    '''
    # archi_data 引用archi的svg代码
    # svg_data 使用archi和绘画非archi的代码

    with open(name, 'w') as f:
        # 文本文档编码格式一般为ANSI，xml编码格式为utf-8
        f.write('<?xml version="1.0" encoding="GBK"?>\n')
        header = f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">\n'
        f.write(header)
        # f.write(f'<rect x="{0}" y="{0}" width="{w}" height="{h}" fill="{"blue"}"/>\n')
        # f.write(f'<rect x="{0.05*h}" y="{0.05*h}" width="{w-0.1*h}" height="{0.8*h}" fill="{"red"}"/>\n')

        # css
        f.write(css_data)


        horizon,y = draw_horizon(0.05 * h + (0.8 * h) * 0.8, 0.05 * h + (0.8 * h) * 0.85, '#0B0B0B', hori_wid)
        mid_shot = draw_mid_shot(0.05 * h + (0.8 * h) * 0.45, 0.05 * h + (0.8 * h) * 0.65, city_colors[3], 2)
        cloud = draw_cloud(0.05 * h + (0.8 * h) * 0.35, 0.05 * h + (0.8 * h) * 0.65, "rgb(193,210,240)")
        mountain = draw_mountain(0.05 * h + (0.8 * h) * 0.25, 0.05 * h + (0.8 * h) * 0.45,mou)
        foreground_data,gap_location,archi_occupy,building_class = foreground(y)
        print(archi_occupy)
        gap_wave_data = draw_gap_wave(gap_location,'blue')
        plant_data = draw_plant(gap_location,y-(0.8 * h) * 0.1,pla,y,5)
        boat_data = draw_boat(gap_location,y,boa)
        outer_data = sign_icon(input_time,icon_path)
        pedestrian_data = draw_pedestrian(gap_location,archi_occupy,building_class, y - (0.8 * h) * 0.15, ped, y, 2)

        f.write(cloud)
        f.write(mountain)
        f.write(mid_shot)

        f.write(foreground_data)
        f.write(plant_data)
        f.write(pedestrian_data)
        f.write(horizon)
        f.write(gap_wave_data)
        f.write(boat_data)
        f.write(outer_data)



        f.write(archi_data)
        footer = f'</svg>\n'
        f.write(footer)

archi_paths,mou,clo,pla,boa,ped = recommend(archi_paths)
svg_path = r"D:\生成艺术\urban_skyline\sketch_ac_0.svg"
css_data = def_css(city_colors)
archi_data = def_archi(archi_paths,mou,clo,pla,boa,ped,icon_path)

create_svg(svg_path, css_data, archi_data)

# web = webdriver.Edge(executable_path=edge_path)
#
# # 模拟浏览器打开svg文件
# print(svg_path)
# web.get(svg_path)