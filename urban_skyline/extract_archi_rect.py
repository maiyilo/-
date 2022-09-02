import js2py
import webbrowser
import os
import json
from selenium import webdriver

# 绝对位置
form_svg_path = r"D:\生成艺术\urban_skyline\form_archi"
svg_path_list = os.listdir(form_svg_path)
print(svg_path_list)
# edge驱动器位置
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedgedriver.exe"

def getBoundingRect_Args(svg_path):
    '''
    svg_path:需要解析的单个svg文件路径
    output:name rect.x rect.y rect.width rect.height
    svg名称 外接矩形的左上角坐标，长宽
    '''

    web = webdriver.Edge(executable_path=edge_path)
    # 模拟浏览器打开svg文件
    print(svg_path)
    web.get(svg_path)

    name = svg_path.split('\\')[-1].split('.')[0]
    javascriptCode_1 = f'''
    var svg1   = document.getElementById("archi_svg_{name}");
    var archi = svg1.getElementById("{name}");
    var rect = archi.getBoundingClientRect();
    return rect.x
    '''
    javascriptCode_2 = f'''
    var svg1   = document.getElementById("archi_svg_{name}");
    var archi = svg1.getElementById("{name}");
    var rect = archi.getBoundingClientRect();
    return rect.y
    '''
    javascriptCode_3 = f'''
    var svg1   = document.getElementById("archi_svg_{name}");
    var archi = svg1.getElementById("{name}");
    var rect = archi.getBoundingClientRect();
    return rect.width
    '''
    javascriptCode_4 = f'''
    var svg1   = document.getElementById("archi_svg_{name}");
    var archi = svg1.getElementById("{name}");
    var rect = archi.getBoundingClientRect();
    return rect.height
    '''

    # js提取svg渲染后的外接矩形
    x = web.execute_script(javascriptCode_1)
    y = web.execute_script(javascriptCode_2)
    width = web.execute_script(javascriptCode_3)
    height = web.execute_script(javascriptCode_4)
    print(f"x={x} y={y} width={width} height={height}")
    web.quit()
    return name,x,y,width,height


# 遍历文件夹的到外接矩形参数字典，key为svg文件名称
# 嵌套的archi svg最小外接矩形位置参数
with open(form_svg_path +'\\'+ "write_json.json", encoding="utf-8") as f:
    rect_args = json.load(f)
keys = rect_args.keys()
for each_path in svg_path_list:
    print(each_path)
    if each_path.split('.')[-1] == "svg" and each_path.split('\\')[-1].split('.')[0] not in keys:
        svg_path = form_svg_path + '\\' + each_path
        name,x,y,widht,height = getBoundingRect_Args(svg_path)
        rect_args[name]=[x,y,widht,height]
with open(form_svg_path +"\\"+ "write_json.json", "w", encoding='utf-8') as f:
    json.dump(rect_args, f, indent=2, sort_keys=False, ensure_ascii=False)  # 写为多行


# webbrowser.register('edge', None, webbrowser.BackgroundBrowser(edge_path))
# browser = webbrowser.get('edge').open(svg_path)

# print(js2py.eval_js('console.log("hello world")'))

# func_js = '''
# function add(a,b){
#     return a+b
# }
# '''
# add = js2py.eval_js(func_js)
# print(add(1,2))
# print(js2py.eval_js('var a = "python";a'))
# # print(js2py.translate_js("console.log('hello world')"))
# js_code = """
# pyimport requests
# console.log('导入成功');
# var response = requests.get('file:///D:/%E7%94%9F%E6%88%90%E8%89%BA%E6%9C%AF/archi/1.svg');
# console.log(response.url)
# console.log(response.content);
# """
# print(js2py.eval_js(js_code))