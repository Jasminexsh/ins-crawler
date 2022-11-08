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
photos_url_list_path_dir = resources_path_dir + 'photos_url_lists.txt'
videos_url_list_path_dir = resources_path_dir + 'videos_url_lists.txt'
# 资源保存路径
photos_resources_path_dir = resources_path_dir + 'photos/'
videos_resources_path_dir = resources_path_dir + 'videos/'

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
next_url = resource_url_template.format(user_id, num, next_max_id)
next_url_request = requests.get(next_url, headers=headers)
next_url_json = next_url_request.json()
next_items = next_url_json['items']
next_more_available = next_url_json['more_available']


# 获取图片url列表
def get_photos_url_list(photos_items):
    photos_url_list = []
    for photos_item in photos_items:
        if 'video_versions' not in photos_item:
            # 单张照片
            if 'image_versions2' in photos_item:
                img_link = photos_item['image_versions2']['candidates'][0]['url']
                photos_url_list.append(img_link)
            # 多张照片
            elif 'carousel_media' in photos_item:
                for photo_carousel_media_item in photos_item['carousel_media']:
                    img_link = photo_carousel_media_item['image_versions2']['candidates'][0]['url']
                    photos_url_list.append(img_link)
    return photos_url_list


# 获取视频url列表
def get_videos_url_list(videos_items):
    videos_url_list = []
    for videos_item in videos_items:
        if 'video_versions' in videos_item:
            video_link = videos_item['video_versions'][0]['url']
            videos_url_list.append(video_link)
    return videos_url_list


# 保存图片url列表文件
def save_photos_url_list_txt(photos_url_list):
    if not os.path.exists(resources_path_dir):
        os.makedirs(resources_path_dir)
    with open(photos_url_list_path_dir, 'a') as file:
        # 追加写文件
        file.write('\n'.join(photos_url_list))
        file.write('\n')


# 保存视频url列表文件
def save_videos_url_list_txt(videos_url_list):
    if not os.path.exists(resources_path_dir):
        os.makedirs(resources_path_dir)
    with open(videos_url_list_path_dir, 'a') as file:
        # 追加写文件
        file.write('\n'.join(videos_url_list))
        file.write('\n')


# 保存图片资源
def save_photos_resources():
    # 判断文件夹中已下载的资源数量 重试时提速
    photos_count = 0
    # 写入文件保存资源
    if not os.path.exists(photos_resources_path_dir):
        os.makedirs(photos_resources_path_dir)
    if len(os.listdir(photos_resources_path_dir)) > 0:
        photos_count = len(os.listdir(photos_resources_path_dir))
    with open(photos_url_list_path_dir, 'r') as file:
        # 遍历文件时加上文件行数索引
        photos_current_count = 0
        for line in file.readlines():
            if photos_current_count < photos_count:
                photos_current_count += 1
                continue
            line = line.strip()
            photos_count += 1
            photos_current_count += 1
            img_request = requests.get(line, headers=headers)
            if 'n.jpg?' in line:
                with open(photos_resources_path_dir + str(photos_count) + ".jpg", mode='wb') as f:
                    print('正在下载第' + str(photos_count) + '张图片')
                    f.write(img_request.content)


# 保存视频资源
def save_videos_resources():
    # 判断文件夹中已下载的资源数量 重试时提速
    videos_count = 0
    # 写入文件保存资源
    if not os.path.exists(videos_resources_path_dir):
        os.makedirs(videos_resources_path_dir)
    if len(os.listdir(videos_resources_path_dir)) > 0:
        videos_count = len(os.listdir(videos_resources_path_dir))
    with open(videos_url_list_path_dir, 'r') as file:
        # 遍历文件时加上文件行数索引
        video_current_count = 0
        for line in file.readlines():
            if video_current_count < videos_count:
                video_current_count += 1
                continue
            line = line.strip()
            videos_count += 1
            video_current_count += 1
            img_request = requests.get(line, headers=headers)
            if 'n.mp4?' in line:
                with open(videos_resources_path_dir + str(videos_count) + ".mp4", mode='wb') as f:
                    print('正在下载第' + str(videos_count) + '段视频')
                    f.write(img_request.content)


if __name__ == '__main__':
    # 获取资源列表
    if (not os.path.exists(photos_url_list_path_dir)) or (os.path.getsize(photos_url_list_path_dir) == 0):
        # 图片资源列表不存在时，新建列表
        save_photos_url_list_txt(get_photos_url_list(first_12_items))
        while next_more_available:
            save_photos_url_list_txt(get_photos_url_list(next_items))
            next_max_id = next_url_request.json()["next_max_id"]
            next_url = resource_url_template.format(user_id, num, next_max_id)
            next_url_request = requests.get(next_url, headers=headers)
            next_items = next_url_request.json()['items']
            next_more_available = next_url_request.json()['more_available']
        save_photos_url_list_txt(get_photos_url_list(next_items))
        print('----图片资源列表创建完毕----')
    else:
        print('----图片资源列表加载完毕----')
    save_photos_resources()

    if (not os.path.exists(videos_url_list_path_dir)) or (os.path.getsize(videos_url_list_path_dir) == 0):
        # 视频资源列表不存在时，新建列表
        save_videos_url_list_txt(get_videos_url_list(first_12_items))
        while next_more_available:
            save_videos_url_list_txt(get_videos_url_list(next_items))
            next_max_id = next_url_request.json()["next_max_id"]
            next_url = resource_url_template.format(user_id, num, next_max_id)
            next_url_request = requests.get(next_url, headers=headers)
            next_items = next_url_request.json()['items']
            next_more_available = next_url_request.json()['more_available']
        save_videos_url_list_txt(get_videos_url_list(next_items))
        print('----视频资源列表创建完毕----')
    else:
        print('----视频资源列表加载完毕----')
    save_videos_resources()
