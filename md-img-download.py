#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import shutil
import requests
import argparse
from pathlib import Path
from urllib.parse import urlparse
from collections import defaultdict

class MarkdownProcessor:
    def __init__(self):
        self.failed_downloads = defaultdict(list)
        self.processed_files = []

    def download_image(self, url, save_path):
        try:
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return True
        except Exception as error:
            print(f"下载图片失败: {url}, 错误: {error}")
            return False

    def process_markdown_file(self, md_file_path, auto_confirm=False, target_path=None, force_delete=False):
        md_path = Path(md_file_path).absolute()
        if not md_path.exists():
            print(f"错误：文件 {md_path} 不存在")
            return False
        
        print(f"\n正在处理文件: {md_path}")
        
        if target_path:
            absolute_path = Path(target_path).absolute()
            relative_path = md_path.relative_to(md_path.parents[len(md_path.parents)-1])
            folder_path = absolute_path / relative_path.parent / md_path.stem
        else:
            folder_name = md_path.stem
            folder_path = md_path.parent / folder_name
        
        folder_path.mkdir(parents=True, exist_ok=True)
        print(f"已创建文件夹: {folder_path}")
        
        img_folder = folder_path / "img"
        img_folder.mkdir(exist_ok=True)
        print(f"已创建图片文件夹: {img_folder}")
        
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(md_path, 'r', encoding='gbk') as f:
                    content = f.read()
            except Exception as e:
                print(f"读取文件失败: {md_path}, 错误: {e}")
                return False
        
        img_pattern = r'!\[.*?\]\((.*?)\)|<img.*?src=["\'](.*?)["\'].*?>'
        img_references = re.findall(img_pattern, content)
        
        updated_content = content
        has_failed_downloads = False
        
        for match in img_references:
            img_path = match[0] or match[1]
            
            if not img_path.strip():
                continue

            if img_path.startswith('http://') or img_path.startswith('https://'):
                print(f"\n发现网络图片: {img_path}")
                
                parsed_url = urlparse(img_path)
                img_name = os.path.basename(parsed_url.path) or "downloaded_image.jpg"
                
                local_img_path = img_folder / img_name
                if self.download_image(img_path, local_img_path):
                    print(f"已下载图片到: {local_img_path}")
                    
                    new_img_relative_path = f"./img/{img_name}"
                    updated_content = updated_content.replace(img_path, new_img_relative_path)
                else:
                    has_failed_downloads = True
                    self.failed_downloads[str(md_path)].append(img_path)
                continue
            
            old_img_abs_path = (md_path.parent / img_path).resolve()
            
            if not old_img_abs_path.exists():
                print(f"警告：图片文件不存在，跳过: {old_img_abs_path}")
                continue
            
            img_name = old_img_abs_path.name
            
            new_img_relative_path = f"./img/{img_name}"
            
            try:
                shutil.copy2(old_img_abs_path, img_folder / img_name)
                print(f"已复制图片: {old_img_abs_path} -> {img_folder / img_name}")
                updated_content = updated_content.replace(img_path, new_img_relative_path)
            except Exception as e:
                print(f"移动图片失败: {old_img_abs_path} -> {img_folder / img_name}, 错误: {e}")
        
        new_md_path = folder_path / md_path.name
        with open(new_md_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"\n已更新并移动Markdown文件: {md_path} -> {new_md_path}")
        
        if has_failed_downloads:
            print(f"由于有图片下载失败，保留原始文件: {md_path}")
            return True
        
        if target_path and not force_delete:
            print(f"由于使用了-p参数，保留原始文件: {md_path}")
            return True
        
        if auto_confirm or force_delete:
            delete_original = 'y'
        else:
            delete_original = input(f"是否删除原始Markdown文件 {md_path}? (y/n): ").lower()
        
        if delete_original == 'y':
            try:
                os.remove(md_path)
                print(f"已删除原始Markdown文件: {md_path}")
            except Exception as e:
                print(f"删除原始文件失败: {e}")
        
        return True

    def find_markdown_files(self, directory_path, recursive=False):
        dir_path = Path(directory_path).absolute()
        if not dir_path.is_dir():
            return []
        
        md_files = []
        
        if recursive:
            for current_dir, _, files in os.walk(dir_path):
                for file in files:
                    if file.lower().endswith(('.md', '.markdown')):
                        md_files.append(Path(current_dir) / file)
        else:
            md_files = list(dir_path.glob('*.md')) + list(dir_path.glob('*.markdown'))
        
        return md_files

    def process_directory(self, directory_path, auto_confirm=False, target_path=None, force_delete=False, recursive=False):
        dir_path = Path(directory_path).absolute()
        if not dir_path.is_dir():
            print(f"错误：{dir_path} 不是有效的目录")
            return
        
        md_files = self.find_markdown_files(dir_path, recursive)
        if not md_files:
            print(f"目录 {dir_path} {'及其子目录' if recursive else ''}中没有找到Markdown文件")
            return
        
        print(f"\n在目录 {dir_path} {'及其子目录' if recursive else ''}中找到 {len(md_files)} 个Markdown文件:")
        for i, md_file in enumerate(md_files, 1):
            print(f"  {i}. {md_file}")
        
        if not auto_confirm and not force_delete:
            confirm = input("\n是否继续处理这些文件? (y/n): ").lower()
            if confirm != 'y':
                print("操作已取消")
                return
        
        for md_file in md_files:
            self.process_markdown_file(md_file, auto_confirm, target_path, force_delete)

    def print_failed_downloads(self):
        if not self.failed_downloads:
            return
        
        print("\n" + "="*50)
        print("图片下载失败汇总:")
        total_failures = 0
        
        for file_path, urls in self.failed_downloads.items():
            print(f"\n文件: {file_path}")
            print(f"失败图片数量: {len(urls)}")
            print("失败图片URL:")
            for i, url in enumerate(urls, 1):
                print(f"  {i}. {url}")
            total_failures += len(urls)
        
        print(f"\n总计: {len(self.failed_downloads)} 个文件中的 {total_failures} 张图片下载失败")
        print("="*50)
    
def main():
    parser = argparse.ArgumentParser(
        description='Markdown图片下载整理工具 v1.0\n\n'
                    '功能：\n'
                    '自动整理Markdown文件中的网络图片到本地相对路径img子文件夹\n',
        formatter_class=argparse.RawTextHelpFormatter,
    )
    
    parser.add_argument(
        'paths', 
        nargs='+', 
        help='Markdown文件路径或包含Markdown文件的目录'
    )
    parser.add_argument(
        '-y', '--yes', 
        action='store_true', 
        help='自动确认所有提示(包括删除原始文件)'
    )
    parser.add_argument(
        '-p', '--path',
        metavar='DIR',
        help='指定目标目录路径，用于存放生成的文件夹(支持绝对路径和相对路径)'
    )
    parser.add_argument(
        '--recursion',
        action='store_true',
        help='递归处理指定文件夹目录中的Markdown文件'
    )
    parser.add_argument(
        '--delete',
        action='store_true',
        help='强制删除原始Markdown文件(即使使用了-p参数)'
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 1.2',
        help='显示版本信息并退出'
    )
    
    args = parser.parse_args()
    
    processor = MarkdownProcessor()
    auto_confirm = args.yes
    target_path = args.path
    force_delete = args.delete
    recursive = args.recursion
    
    for path in args.paths:
        path_obj = Path(path).absolute()
        
        if path_obj.is_dir():
            processor.process_directory(path_obj, auto_confirm, target_path, force_delete, recursive)
        else:
            if '*' in path or '?' in path:
                import glob
                md_files = glob.glob(path)
                md_files = list(set(str(Path(f).absolute()) for f in md_files))
                
                if not md_files:
                    print(f"警告：没有找到匹配 {path} 的文件")
                    continue
                
                print(f"\n找到 {len(md_files)} 个匹配 {path} 的文件:")
                for i, md_file in enumerate(md_files, 1):
                    print(f"  {i}. {md_file}")
                
                if not auto_confirm and not force_delete:
                    confirm = input("\n是否继续处理这些文件? (y/n): ").lower()
                    if confirm != 'y':
                        print("操作已取消")
                        continue
                
                for md_file in md_files:
                    processor.process_markdown_file(md_file, auto_confirm, target_path, force_delete)
            else:
                processor.process_markdown_file(path_obj, auto_confirm, target_path, force_delete)
    
    processor.print_failed_downloads()
    print("\n所有文件处理完成!")

if __name__ == "__main__":
    main()