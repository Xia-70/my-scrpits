# my-scrpits
一个自动整理Markdown文件中的网络图片到本地相对路径img子文件夹

usage: md-img-download.py [-h] [-y] [-p DIR] [--recursion] [--delete] [-v] paths [paths ...]

positional arguments:
  paths               Markdown文件路径或包含Markdown文件的目录

options:
  -h, --help          show this help message and exit
  -y, --yes           自动确认所有提示(包括删除原始文件)
  -p DIR, --path DIR  指定目标目录路径，用于存放生成的文件夹(支持绝对路径和相对路径)
  --recursion         递归处理指定文件夹目录中的Markdown文件
  --delete            强制删除原始Markdown文件(即使使用了-p参数)
  -v, --version       显示版本信息并退出
