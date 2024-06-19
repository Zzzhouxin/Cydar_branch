"""
标记Dscan模块扫描获取的banner结果
版本库来源于CPE库文件、爬虫爬取的官网release history、本地的识别结果版本库
"""
import json
import os
import xml.etree.ElementTree as ET
import pandas as pd

# config
CPE_path = "./pip/official-cpe-dictionary_v2.3.xml"
release_history_path = r"C:\Users\周鑫\Desktop\EasySpider_windows_x64\Data"
local_response_path = './pip/Collector.json'

golab_product = ['nginx', 'jetty', 'iis', 'lighttpd', 'tengine',
                 'http server', 'openresty', 'boa', 'rompager', 'kestrel']

# golab_product = ['openresty']

# 初始化版本合并结果
version_res = {}
for item in golab_product:
    version_res[item] = list()


def merge_version_from_CPE(CPE_path, version_res, product):
    """
    :param CPE_path: CPE的输入路径
    :param version_res: 合并输出的结果
    :param product: 合并的容器类型
    :return: void
    """

    print("@INFO：开始合并CPE版本库" + product)

    try:
        with open(CPE_path, "r", encoding="utf-8") as file:
            xml_content = file.read()

            # 使用ElementTree解析XML
            root = ET.fromstring(xml_content)

            # 处理XML内容
            cpe_items = root.findall('.//{http://cpe.mitre.org/dictionary/2.0}cpe-item')
            # 遍历cpe-item元素，并输出相关信息
            for cpe_item in cpe_items:
                name = cpe_item.get('name')

                # 使用字符串分割来提取产品和版本信息
                # cpe: / < part >: < vendor >: < product >: < version >: < update >: < edition >: < language >
                components = name.split(':')
                _vendor = components[2]
                _product = components[3]
                _version = components[4]
                _title = cpe_item.find('.//{http://cpe.mitre.org/dictionary/2.0}title').text
                _references = cpe_item.findall('.//{http://cpe.mitre.org/dictionary/2.0}reference')

                # Todo 处理CPE库里名称不统一的问题
                if product == "http server":
                    new_product = "http_server"

                    if _product == new_product and _version not in version_res[product]:
                        version_res[product].append(_version)

                else:
                    if _product == product and _version not in version_res[product]:
                        version_res[product].append(_version)

    except FileNotFoundError:
        print("指定的XML文件不存在或路径错误。")
    except IOError:
        print("无法打开或读取XML文件。")


def merge_version_from_release_history(release_history_path, version_res, product=None):

    print("@INFO：开始合并release history版本库")

    file_list = os.listdir(release_history_path)

    # 循环遍历每个文件
    for file_name in file_list:

        if file_name in golab_product:
            file_path = os.path.join(release_history_path, file_name)

            # 确保是 Excel 文件
            for xlsx_file in os.listdir(file_path):

                if xlsx_file.endswith('.xlsx') or xlsx_file.endswith('.xls'):
                    file_path = os.path.join(file_path, xlsx_file)

                    # 使用 pandas 读取 Excel 文件
                    try:
                        df = pd.read_excel(file_path)
                        print(f"读取文件：{file_name}")
                        # 这里可以对 df 进行你需要的处理
                        for _ in df.iloc[:, 0]:
                            if _ not in version_res[file_name]:
                                version_res[file_name].append(_)

                    except Exception as e:
                        print(f"读取文件 {file_name} 失败: {e}")


def merge_version_from_local_response(local_response_path, version_res, product):

    print("@INFO：开始合并本地识别结果版本库" + product)

    with open(local_response_path, mode='r', encoding='utf-8') as f:
        collector = json.load(f)

        for _version in collector[product].keys():
            if _version != "no_version" and _version not in version_res[product]:
                version_res[product].append(_version)


if __name__ == '__main__':

    # 用爬取的release history来更新版本库
    merge_version_from_release_history(release_history_path=release_history_path, version_res=version_res)

    for item in golab_product:
        # 用本地的识别结果库来更新版本库
        merge_version_from_local_response(local_response_path=local_response_path, version_res=version_res,
                                          product=item)

        # 用CPE更新版本库
        merge_version_from_CPE(CPE_path=CPE_path, version_res=version_res, product=item)

    # 使用Series对象来存储字典的值
    series_dict = {key: pd.Series(value) for key, value in version_res.items()}

    # 创建一个pandas的DataFrame
    df = pd.DataFrame(series_dict)

    # 将DataFrame写入到Excel文件
    output_file = './pip/new_data.xlsx'
    df.to_excel(output_file, index=False)

    print(version_res)
