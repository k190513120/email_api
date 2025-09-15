#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音视频监控功能模块
用于获取抖音博主的视频信息并同步到飞书多维表格
"""

import requests
import json
import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from baseopensdk import BaseClient
from baseopensdk.api.base.v1 import *

class DouyinVideoSync:
    def __init__(self, personal_base_token: str):
        """
        初始化抖音视频同步器
        
        Args:
            personal_base_token: 飞书个人基础Token
        """
        self.personal_base_token = personal_base_token
        self.douyin_api_base = "https://tiktok-api-miaomiaocompany-c35bd5a6.koyeb.app"
        self.feishu_client = None
        
    def extract_sec_user_id(self, douyin_url: str) -> str:
        """
        从抖音主页URL中提取sec_user_id
        
        Args:
            douyin_url: 抖音主页链接
            
        Returns:
            sec_user_id: 用户的sec_user_id
            
        Raises:
            ValueError: 如果URL格式不正确
        """
        # 匹配抖音用户URL中的sec_user_id
        pattern = r'https://www\.douyin\.com/user/([A-Za-z0-9_-]+)'
        match = re.search(pattern, douyin_url)
        
        if not match:
            raise ValueError(f"无法从URL中提取sec_user_id: {douyin_url}")
            
        return match.group(1)
    
    def parse_bitable_url(self, bitable_url: str) -> Tuple[str, str]:
        """
        解析飞书多维表格URL，提取app_token和table_id
        
        Args:
            bitable_url: 飞书多维表格链接
            
        Returns:
            tuple: (app_token, table_id)
            
        Raises:
            ValueError: 如果URL格式不正确
        """
        # 匹配飞书多维表格URL中的app_token和table_id
        pattern = r'https://[^/]+/base/([A-Za-z0-9]+)\?table=([A-Za-z0-9]+)'
        match = re.search(pattern, bitable_url)
        
        if not match:
            raise ValueError(f"无法解析多维表格URL: {bitable_url}")
            
        return match.group(1), match.group(2)
    
    def fetch_douyin_videos(self, sec_user_id: str, count: int = 20, max_cursor: int = 0) -> Dict:
        """
        获取抖音博主的视频信息
        
        Args:
            sec_user_id: 用户的sec_user_id
            count: 获取视频数量
            max_cursor: 游标位置
            
        Returns:
            dict: API响应数据
            
        Raises:
            requests.RequestException: 请求失败
        """
        url = f"{self.douyin_api_base}/api/douyin/web/fetch_user_post_videos"
        params = {
            'sec_user_id': sec_user_id,
            'max_cursor': max_cursor,
            'count': count
        }
        
        headers = {
            'accept': 'application/json'
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise requests.RequestException(f"获取抖音视频失败: {e}")
    
    def init_feishu_client(self, app_token: str):
        """
        初始化飞书BaseOpenSDK客户端
        
        Args:
            app_token: 应用Token
        """
        try:
            self.feishu_client = BaseClient.builder() \
                .app_token(app_token) \
                .personal_base_token(self.personal_base_token) \
                .build()
            print("飞书客户端初始化成功")
        except Exception as e:
            raise Exception(f"飞书客户端初始化失败: {e}")
    
    def get_existing_records(self, table_id: str) -> List[Dict]:
        """
        获取多维表格中已存在的记录
        
        Args:
            table_id: 表格ID
            
        Returns:
            list: 已存在的记录列表
        """
        all_records = []
        page_token = None
        
        try:
            while True:
                # 构造请求对象
                request_builder = ListAppTableRecordRequest.builder().table_id(table_id).page_size(500)
                if page_token:
                    request_builder.page_token(page_token)
                
                request = request_builder.build()
                
                # 发起请求
                response = self.feishu_client.base.v1.app_table_record.list(request)
                
                if response.code == 0:
                    records = getattr(response.data, 'items', [])
                    # 转换为字典格式
                    if records:
                        for record in records:
                            all_records.append({
                                'record_id': record.record_id,
                                'fields': record.fields
                            })
                    
                    page_token = getattr(response.data, 'page_token', None)
                    if not page_token:
                        break
                else:
                    print(f"获取记录失败: {response.msg}")
                    break
                    
        except Exception as e:
            print(f"获取已存在记录失败: {e}")
            
        return all_records
    
    def format_video_data(self, video_info: Dict) -> Dict:
        """
        格式化视频数据为多维表格格式
        
        Args:
            video_info: 视频信息
            
        Returns:
            dict: 格式化后的数据
        """
        # 提取视频基本信息
        aweme_id = video_info.get('aweme_id', '')
        desc = video_info.get('desc', '')
        create_time = video_info.get('create_time', 0)
        
        # 转换时间戳为可读格式
        if create_time:
            create_time_str = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d %H:%M:%S')
        else:
            create_time_str = ''
        
        # 提取作者信息
        author = video_info.get('author', {})
        author_name = author.get('nickname', '')
        author_id = author.get('sec_uid', '')
        
        # 提取统计信息
        statistics = video_info.get('statistics', {})
        digg_count = statistics.get('digg_count', 0)  # 点赞数
        comment_count = statistics.get('comment_count', 0)  # 评论数
        share_count = statistics.get('share_count', 0)  # 分享数
        play_count = statistics.get('play_count', 0)  # 播放数
        
        # 提取视频下载链接
        video_info_detail = video_info.get('video', {})
        play_addr = video_info_detail.get('play_addr', {})
        url_list = play_addr.get('url_list', [])
        video_url = url_list[2] if len(url_list) > 2 else f"https://www.douyin.com/video/{aweme_id}"
        
        # 提取短视频语音URL
        music_info = video_info.get('music', {})
        play_url_info = music_info.get('play_url', {})
        audio_url = play_url_info.get('uri', '')
        
        # 提取封面图片
        cover_info = video_info_detail.get('origin_cover', {})
        cover_url = ''
        if cover_info and cover_info.get('url_list'):
            cover_url = cover_info['url_list'][0] if cover_info['url_list'] else ''
        
        return {
            '视频ID': aweme_id,
            '描述': desc,
            '点赞': digg_count,
            '评论': comment_count,
            '收藏': 0,  # API中没有收藏数，设为0
            '转发': share_count,
            '视频下载链接': video_url,
            'SEC': author_id,
            '视频封面': cover_url,
            '作者': author_name,
            '短视频语音 URL': audio_url,
            '视频创建时间': create_time_str
        }
    
    def add_record_to_table(self, table_id: str, record_data: Dict) -> bool:
        """
        添加记录到多维表格
        
        Args:
            table_id: 表格ID
            record_data: 记录数据
            
        Returns:
            bool: 是否成功
        """
        try:
            # 构造请求对象
            request = CreateAppTableRecordRequest.builder() \
                .table_id(table_id) \
                .request_body(AppTableRecord.builder().fields(record_data).build()) \
                .build()
            
            # 发起请求
            response = self.feishu_client.base.v1.app_table_record.create(request)
            
            if response.code == 0:
                return True
            else:
                print(f"添加记录失败: {response.msg}")
                return False
                
        except Exception as e:
            print(f"添加记录到表格失败: {e}")
            return False
    
    def sync_videos_to_table(self, douyin_url: str, bitable_url: str, count: int = 20) -> Dict:
        """
        同步抖音视频到飞书多维表格
        
        Args:
            douyin_url: 抖音主页链接
            bitable_url: 飞书多维表格链接
            count: 获取视频数量
            
        Returns:
            dict: 同步结果
        """
        result = {
            'success': False,
            'message': '',
            'total_videos': 0,
            'new_videos': 0,
            'skipped_videos': 0,
            'failed_videos': 0,
            'videos': []
        }
        
        try:
            # 1. 提取sec_user_id
            sec_user_id = self.extract_sec_user_id(douyin_url)
            print(f"提取到sec_user_id: {sec_user_id}")
            
            # 2. 解析多维表格URL
            app_token, table_id = self.parse_bitable_url(bitable_url)
            print(f"解析到app_token: {app_token}, table_id: {table_id}")
            
            # 3. 初始化飞书客户端
            self.init_feishu_client(app_token)
            
            # 4. 获取已存在的记录
            existing_records = self.get_existing_records(table_id)
            existing_video_ids = set()
            for record in existing_records:
                fields = record.get('fields', {})
                video_id = fields.get('视频ID')
                if video_id:
                    existing_video_ids.add(video_id)
            print(f"已存在 {len(existing_video_ids)} 条视频记录")
            
            # 5. 获取抖音视频信息
            video_data = self.fetch_douyin_videos(sec_user_id, count)
            
            if video_data.get('code') != 200:
                result['message'] = f"获取抖音视频失败: {video_data.get('message', '未知错误')}"
                return result
            
            aweme_list = video_data.get('data', {}).get('aweme_list', [])
            result['total_videos'] = len(aweme_list)
            
            print(f"获取到 {len(aweme_list)} 个视频")
            
            # 6. 处理每个视频
            for video_info in aweme_list:
                video_id = video_info.get('aweme_id')
                
                # 检查是否已存在
                if video_id in existing_video_ids:
                    result['skipped_videos'] += 1
                    print(f"视频 {video_id} 已存在，跳过")
                    continue
                
                # 格式化视频数据
                formatted_data = self.format_video_data(video_info)
                
                # 添加到表格
                if self.add_record_to_table(table_id, formatted_data):
                    result['new_videos'] += 1
                    result['videos'].append(formatted_data)
                    print(f"成功添加视频: {formatted_data['描述'][:50]}...")
                else:
                    result['failed_videos'] += 1
                    print(f"添加视频失败: {video_id}")
                
                # 添加延迟避免请求过快
                time.sleep(0.5)
            
            result['success'] = True
            result['message'] = f"同步完成: 总计{result['total_videos']}个视频，新增{result['new_videos']}个，跳过{result['skipped_videos']}个，失败{result['failed_videos']}个"
            
        except Exception as e:
            result['message'] = f"同步失败: {str(e)}"
            print(f"同步过程中出错: {e}")
        
        return result

def main():
    """
    主函数，用于测试
    """
    # 测试参数
    douyin_url = "https://www.douyin.com/user/MS4wLjABAAAA5zM-9y7PPDEw09BMuCSfEbuDq-B0y1z9EMPjL4GNPUiTsgR1KquzCK69paBdt_gW?from_tab_name=main"
    bitable_url = "https://larkcommunity.feishu.cn/base/SU5ObtCiZaMhiVsXNrbcuJ2hnYd?table=tblaeDuGK2Tm3vC0&view=vewgd2kKP7"
    personal_base_token = "pt-sWz-h22qUT_0OppCTI49awOweB5fHUS7ZkvPxmiZAQAAA8BNIAPAgEQH6ppI"
    count = 5
    
    # 创建同步器
    sync = DouyinVideoSync(personal_base_token)
    
    # 执行同步
    result = sync.sync_videos_to_table(douyin_url, bitable_url, count)
    
    # 输出结果
    print("\n=== 同步结果 ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()