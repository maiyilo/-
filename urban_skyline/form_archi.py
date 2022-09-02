import random
import os
import re
from lxml import etree
import cv2
import numpy as np

# 画布
w = 1000
h = 1000

archi_path = 'archi'
path_list = os.listdir(archi_path)
print(path_list)

# 定义解析器,
parser = etree.XMLParser(encoding = "utf-8")

# 根据archi路径导入到<defs>中
def def_archi(svg_path):
    # archi_path:archi的svg文件路径
    # 返回提取的archi svg代码  <defs></defs>

    archi_data = "<defs>\n"
    # 传入两个参数，第一个参数是文件名，第二个参数是解析器。
    tree = etree.parse(svg_path, parser=parser)  # 查看解析出的tree的内容
    svg_text = etree.tostring(tree, encoding='utf-8').decode('utf-8')
    svg_root = etree.XML(svg_text)

    name = svg_path.split('/')[-1].split(".")[0]
    archi_data += f"<g id=\'archi_{name}\'>\n"
    for child in svg_root:
        if child.tag.split('}')[-1] != "style":
            data = etree.tostring(child,encoding="utf-8").decode('utf-8')+"\n"

            # 通过正则表达式过滤fill stroke属性
            data = re.sub('stroke:.*?;', '', data)
            data = re.sub('stroke-width:.*?;', '', data)
            data = re.sub('fill:.*?;', '', data)
            data = re.sub('stroke=".*?"', '', data)
            data = re.sub('stroke-width=".*?"', '', data)
            archi_data += re.sub('fill=".*?"', '', data)

    # 添加交互title
    archi_data += f"<title>archi_{name}</title>\n"
    archi_data += "</g>\n"
    archi_data += "</defs>\n"
    return archi_data


# 调用archi的代码
def use_archi(svg_path):
    # svg_path:archi路径
    # 返回use_data,也就是svg的调用archi代码

    name = svg_path.split('/')[-1].split(".")[0]

    # viewBox铺满以捕捉到archi全貌,width,height固定为1000*1000大小,尽量之后都使archi缩小而不是放大（会丢失部分）
    use_data = f'<svg id="{name}" xml:space="preserve">\n'

    use_data += f'<use class="ic-2" xlink:href="#archi_{name}"/>'

    use_data += "</svg>\n"

    return use_data

def create_svg(svg_path,archi_data,use_data,output_path):
    '''
    svg_path:archi路径
    archi_data 引用archi的svg代码
    svg_data 使用archi和绘画非archi的代码
    output_path 辅助svg文件输出到output_path
    '''

    name = svg_path.split('/')[-1].split(".")[0]
    with open(output_path + f"/{name}.svg", 'w') as f:
        # 文本文档编码格式一般为ANSI，xml编码格式为utf-8
        f.write('<?xml version="1.0" encoding="GBK"?>\n')
        header = f'<svg id="archi_svg_{name}" width="8000" height="8000" viewBox="0 0 8000 8000" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">\n'
        f.write(header)
        f.write('<style xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" type="text/css">'
                'use.ic-1 { fill: skyblue; }use.ic-2 { fill:none; stroke:#42C2FF;stroke-width:2}</style>')
        f.write(use_data)
        f.write(archi_data)

        footer = f'</svg>\n'
        f.write(footer)

# 遍历每个svg文件创建辅助svg文件
def each_archi(path_list,output_path):
    '''
    archi_path:svg文件路径列表
    所有辅助svg文件输出到output_path
    '''
    for each_path in path_list:
        if each_path.split('.')[-1] == "svg":
            print(f"正在处理{archi_path+'/'+each_path}")
            archi_data = def_archi(archi_path+'/'+each_path)
            use_data = use_archi(archi_path+'/'+each_path)
            create_svg(archi_path+'/'+each_path,archi_data,use_data,output_path)

each_archi(path_list,'form_archi')
'''
javascript 解析二级嵌套的svg外接矩形区域，rect.x rect.y rect.width rect.height
传入为作画程序的archi引用viewBox参数
var svg1   = document.getElementById("svg1");
var archi = svg1.getElementById("archi");
var rect = archi.getBoundingClientRect();
console.log(rect.x)
console.log(rect.y)
console.log(rect.width);
console.log(rect.height);
'''