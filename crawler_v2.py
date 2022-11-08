import requests
import os
import argparse

# HTTP Header
headers = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 105.0.0.11.118 (iPhone11,8; iOS 12_3_1; en_US; en-US; scale=2.00; 828x1792; 165586599)'}

# 命令行参数
parser = argparse.ArgumentParser()
parser.add_argument('-u', '--username', type=str)
args = parser.parse_args()
username = args.username

# 用户profile url
user_profile_url = 'https://www.instagram.com/api/v1/users/web_profile_info/?username={}'.format(username)
# 资源url模板
resource_url_template = 'https://www.instagram.com/api/v1/feed/user/{}/?current_count={}&max_id={}'
# 下载资源路径
resources_path_dir = 'resources/{}/'.format(username)
# 资源列表文件路径
url_list_txt_path_dir = 'url_lists_{}.txt'.format(username)

# 前12个静态加载资源元数据
first_12_url_template = 'https://www.instagram.com/api/v1/feed/user/{}/username/?count=12'
first_12_url = first_12_url_template.format(username)
first_12_url_request = requests.get(first_12_url, headers=headers)
first_12_url_json = first_12_url_request.json()
first_12_items = first_12_url_json['items']

num = 12
user_id = first_12_url_json['user']['pk']
max_id = first_12_url_json['next_max_id']

# 初始化剩余动态加载资源元数据
next_max_id = max_id
next_url = resource_url_template.format(user_id, num, max_id)
next_url_request = requests.get(next_url, headers=headers)
next_url_json = next_url_request.json()
next_items = next_url_json['items']
next_more_available = next_url_json['more_available']


# 获取资源url列表
def get_url_list(items):
    url_list = []
    for item in items:
        # 帖子为视频
        if 'video_versions' in item:
            video_link = item['video_versions'][0]['url']
            url_list.append(video_link)
        # 帖子为单张照片
        elif 'image_versions2' in item:
            img_link = item['image_versions2']['candidates'][0]['url']
            url_list.append(img_link)
        # 帖子为多张照片
        else:
            if 'carousel_media' in item:
                for item_carousel in item['carousel_media']:
                    img_link = item_carousel['image_versions2']['candidates'][0]['url']
                    url_list.append(img_link)
    return url_list


# 保存资源url列表
def save_url_list_txts(url_lists):
    with open(url_list_txt_path_dir, 'a') as file:
        # 追加写文件
        file.write('\n'.join(url_lists))
        file.write('\n')


# 保存资源
def save_resources():
    # 判断文件夹中已下载的资源数量 重试时提速
    count = 0
    # 写入文件保存资源
    if not os.path.exists(resources_path_dir):
        os.makedirs(resources_path_dir)
    if len(os.listdir(resources_path_dir)) > 0:
        count = len(os.listdir(resources_path_dir))
    with open(url_list_txt_path_dir, 'r') as file:
        # 遍历文件时加上文件行数索引
        current_count = 0
        for line in file.readlines():
            if current_count < count:
                current_count += 1
                continue
            line = line.strip()
            count += 1
            current_count += 1
            img_request = requests.get(line, headers=headers)
            if 'n.mp4?' in line:
                with open(resources_path_dir + str(count) + ".mp4", mode='wb') as f:
                    print('正在下载第' + str(count) + '段视频')
                    f.write(img_request.content)
            elif 'n.jpg?' in line:
                with open(resources_path_dir + str(count) + ".jpg", mode='wb') as f:
                    print('正在下载第' + str(count) + '张图片')
                    f.write(img_request.content)


if __name__ == '__main__':
    # 获取资源列表
    if not os.path.exists(url_list_txt_path_dir) or os.path.getsize(url_list_txt_path_dir) == 0:
        # 资源列表不存在时，新建列表
        save_url_list_txts(get_url_list(first_12_items))
        while next_more_available:
            save_url_list_txts(get_url_list(next_items))
            next_max_id = next_url_request.json()["next_max_id"]
            next_url = resource_url_template.format(user_id, num, next_max_id)
            next_url_request = requests.get(next_url, headers=headers)
            next_items = next_url_request.json()['items']
            next_more_available = next_url_request.json()['more_available']
        save_url_list_txts(get_url_list(next_items))
        print('----资源列表创建完毕----')
    else:
        print('----资源列表加载完毕----')
    # 下载资源
    save_resources()
