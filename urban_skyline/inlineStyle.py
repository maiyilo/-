import random
import json
import os
import re
from lxml import etree
from selenium import webdriver
import cv2
import numpy as np

import random
import os
import re
from lxml import etree
import cv2
import numpy as np

path = 'archi'
archi_path = os.listdir(path)
for i in range(len(archi_path)):
    archi_path[i] = path + '/' + archi_path[i]

# archi的svg文件写成内联样式
def inline_style(root_node,css):
    # if root_node.get('id') in id_list:
    #     result_list.append(root_node.get('class'))
    cls = root_node.get('class')
    if cls is not None:
        root_node.attrib['style'] = css[cls]


    # 遍历每个子节点
    children_node = root_node.getchildren()
    if len(children_node) == 0:
        return
    for child in children_node:
        if child.tag.split('}')[-1] == "style":
            root_node.remove(child)
        else:
            inline_style(child,css)
    return

def main(path):
    '''
    :param path: 文件路径
    :return: 返回找到的css字典
    '''
    # 定义解析器
    parser = etree.XMLParser(encoding="utf-8")
    # 传入两个参数，第一个参数是文件名，第二个参数是解析器。
    tree = etree.parse(path, parser=parser)  # 查看解析出的tree的内容
    svg_text = etree.tostring(tree, encoding='utf-8').decode('utf-8')
    svg_root = etree.XML(svg_text)
    root = etree.HTML(svg_text)
    file_name = path.split('/')[-1].split('.')[0]

    css = {}

    # 寻找<style>文本
    try:
        style = root.xpath('//style/text()')[0].split('}')
        for i in range(len(style)):
            style[i] = style[i].replace('\n', '').replace(' ', '')
            try:
                cls = style[i].split('{')[0].split(',')
                attr = style[i].split('{')[1]
                for each in cls:
                    name = each.split('.')[1]
                    if name not in css.keys():
                        css[name] = attr
                    else:
                        css[name] = css[name] + attr
            except:
                continue
    except:
        pass

    inline_style(svg_root, css)
    svg_text = etree.tostring(svg_root, encoding='utf-8').decode('utf-8')
    with open(f'new_archi/{file_name}.svg', 'w') as f:
        f.write('<?xml version="1.0" encoding="GBK"?>\n')
        f.write(svg_text)

for each in archi_path:
    print(each)
    main(each)


# # 遍历所有id在id_list内的节点
# def extract_classes(root_node,id_list, result_list):
#     global unique_id
#     if root_node.get('id') in id_list:
#         result_list.append(root_node.get('class'))
#
#     # 遍历每个子节点
#     children_node = root_node.getchildren()
#     if len(children_node) == 0:
#         return
#     for child in children_node:
#         extract_classes(child, id_list, result_list)
#
# deep_classes = []
# # 定义解析器
# parser = etree.XMLParser(encoding = "GBK")
# # 传入两个参数，第一个参数是文件名，第二个参数是解析器。
# tree = etree.parse('building2_new.svg', parser=parser)  # 查看解析出的tree的内容
# svg_text = etree.tostring(tree, encoding='utf-8').decode('utf-8')
# svg_root = etree.XML(svg_text)
# root = etree.HTML(svg_text)
#
# # 深色组内的元素id列表
# deep = root.xpath('//archi/deep/ele/text()')[0].split(',')
# extract_classes(root, deep, deep_classes)
# name = 'building2_new.svg'.split('/')[-1].split(".")[0]
#
# # 递归处理所有子孙节点
# def replace(each_node,color):
#     try:
#         attrib = each_node.attrib['style']
#         attr = re.findall('fill:.*?;', attrib)
#         if len(attr) != 0 and attr[0].split('fill:')[1].split(";")[0] != 'none':
#             # 通过正则表达式过滤fill stroke属性
#             attrib = re.sub('fill:.*?;', f'fill:{color};', attrib)
#         attr = re.findall('stroke:.*?;', attrib)
#         if len(attr) != 0 and attr[0].split('stroke:')[1].split(";")[0] != 'none':
#             attrib = re.sub("stroke:.*?;", f'stroke:{color};', attrib)
#         each_node.attrib['style'] = attrib
#     except:
#         pass
#
#     # 遍历每个子节点
#     children_node = each_node.getchildren()
#     if len(children_node) == 0:
#         return
#     for child in children_node:
#         replace(child, color)
#
#
# # 深色部分
# for each_cls in deep_classes:
#     node = svg_root.xpath(f"//*[@class='{each_cls}']")
#     for each_node in node:
#         replace(each_node,"red")
#
# with open('building2_news.svg', 'w') as f:
#     f.write('<?xml version="1.0" encoding="GBK"?>\n')
#     svg_text = etree.tostring(svg_root, encoding='utf-8').decode('utf-8')
#     f.write(svg_text)
