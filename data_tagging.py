import json
import re

import pandas as pd
from bs4 import BeautifulSoup

# 全局初始化一个sum用来记录有多少识别成web容器的数据
WebContainer_sum = 0
WebContainer_sum_hasName = 0


def get_dscan_list(detect_list):
    res_list = []
    for i in range(len(detect_list)):
        res_list.append(detect_list[i]['banner'])

    return res_list


def parse_dscan_list(banner_list):
    res_list = []
    for i in range(len(banner_list)):
        new_banner = BeautifulSoup(banner_list[i], 'html.parser')
        res_list.append(new_banner.get_text())

    return res_list


def get_product_version(dscan_list, product):
    data_frame = pd.read_excel('./pip/data.xlsx')

    try:
        version_repository = data_frame[product]

        found_version_keywords = []
        for i in range(len(dscan_list)):
            for key_word in version_repository:
                pattern = re.escape(str(key_word))  # 转义特殊字符，避免正则表达式匹配问题
                if re.search(r'\b' + pattern + r'\b', str(dscan_list[i]).lower(), flags=re.IGNORECASE) and \
                        key_word not in found_version_keywords:
                    found_version_keywords.append(key_word)

        print("查找到的版本关键字为：", found_version_keywords)

        return found_version_keywords

    except KeyError:
        # 先不写回本地结果
        print("版本库不存在对应容器")

        return None


def get_product_name(dscan_list):
    patter = re.compile(r'(?i)(?<=\r\nServer: ).*?(?=\r\n)')
    banner_result = []
    for i in range(len(dscan_list)):
        banner = patter.search(str(dscan_list[i]))
        if banner and banner.group(0) not in banner_result:
            banner_result.append(banner.group(0))

    return banner_result


def process_data(dscan_list, app_data=None):
    global WebContainer_sum
    global WebContainer_sum_hasName

    banner_result = get_product_name(dscan_list)

    if banner_result:
        return True


if __name__ == "__main__":

    with open('dscan_output.json', 'r+', encoding='utf-8') as f:
        for line in f:
            json_data = json.loads(line)
            port_list = json_data['port_list']
            # 拿到一条IP-json数据，遍历所有的port_list
            for i in range(len(port_list)):
                port_data = port_list[i]

                # 判断dscan_data字段和app_list是否为空
                try:
                    if len(port_data['dscan_data']['http_server_detect_list']):
                        dscan_list = get_dscan_list(port_data['dscan_data']['http_server_detect_list'])
                        # 用bs4解析报文
                        dscan_list = parse_dscan_list(dscan_list)

                        if dscan_list:
                            WebContainer_sum += 1

                        # 遍历app_list
                        Flag = False

                        for i in range(len(port_data['app_list'])):
                            Flag = Flag or process_data(dscan_list)

                        if Flag:
                            WebContainer_sum_hasName += 1


                except KeyError:
                    # 先不写回本地结果
                    print("dscan_data或app_list读取失败")

    print(WebContainer_sum)
    print(WebContainer_sum_hasName)
