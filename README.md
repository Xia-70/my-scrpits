# my-scrpits

## 简介
`md-img-download.py` 是一个用于自动整理 Markdown 文件中网络图片的脚本，可将网络图片下载到本地相对路径并更新 Markdown 文件中的图片引用路径。

## 版本
v1.0

## 功能
- 自动下载 Markdown 文件中的网络图片
- 将图片保存到本地 `img` 子文件夹
- 更新 Markdown 文件中的图片引用为相对路径
- 支持递归处理目录中的多个 Markdown 文件

## 使用说明
usage: md-img-download.py [-h] [-y] [-p DIR] [--recursion] [--delete] [-v] paths [paths ...]

### 参数说明
| 参数 | 描述 |
|------|------|
| `paths` | Markdown 文件路径或包含 Markdown 文件的目录 |
| `-h`, `--help` | 显示帮助信息并退出 |
| `-y`, `--yes` | 自动确认所有提示（包括删除原始文件） |
| `-p DIR`, `--path DIR` | 指定目标目录路径（支持绝对路径和相对路径） |
| `--recursion` | 递归处理指定文件夹中的 Markdown 文件 |
| `--delete` | 强制删除原始 Markdown 文件（即使使用了 `-p` 参数） |
| `-v`, `--version` | 显示版本信息并退出 |
