# STL到GLB转换器

一个基于Python的轻量级自动转换系统，能够监控指定目录中的STL文件，自动将其转换为GLB格式。

## 功能特点

- 自动监控目录中的新STL文件
- 使用trimesh库将STL文件转换为GLB格式
- 将转换后的文件输出到指定目录
- 可作为后台服务运行，无需人工干预
- 跨平台支持（Windows、Linux、macOS）
- 资源占用低
- 支持批量处理和多线程转换
- 可通过命令行或配置文件进行配置
- 支持源文件备份功能
- 详细的操作日志记录

## 系统要求

- Python 3.7或更高版本
- `requirements.txt`中列出的依赖库

## 安装

1. 克隆此仓库或下载源代码
2. 安装所需依赖：

```bash
pip install -r requirements.txt
```

3. 对于Windows服务安装，请下载[NSSM](https://nssm.cc/)并将其添加到PATH中

## 使用方法

### 命令行界面

转换器提供了全面的命令行界面：

```bash
python cli.py [命令] [选项]
```

可用命令：

- `watch`：监控目录中的STL文件并转换它们
- `batch`：一次性转换目录中的所有STL文件
- `config`：管理配置
- `service`：管理服务安装和控制

#### Watch命令

监控目录中的新STL文件并自动转换：

```bash
python cli.py watch --input 输入目录 --output 输出目录 --recursive
```

选项：
- `--input`：要监控的输入目录
- `--output`：GLB文件的输出目录
- `--recursive`：递归监控子目录
- `--config`：配置文件路径

#### Batch命令

一次性转换目录中的所有STL文件：

```bash
python cli.py batch --input 输入目录 --output 输出目录 --workers 4
```

选项：
- `--input`：包含STL文件的输入目录
- `--output`：GLB文件的输出目录
- `--workers`：用于并行处理的工作线程数
- `--recursive`：递归扫描子目录
- `--config`：配置文件路径

#### Config命令

管理配置：

```bash
python cli.py config --set input_directory=新输入目录 --set recursive_scan=true
```

选项：
- `--set`：设置配置值（键=值）
- `--get`：获取配置值
- `--reset`：重置配置为默认值
- `--show`：显示当前配置
- `--file`：配置文件路径

#### Service命令

管理服务安装：

```bash
python cli.py service --install
```

选项：
- `--install`：安装为服务
- `--uninstall`：卸载服务
- `--start`：启动服务
- `--stop`：停止服务
- `--status`：检查服务状态
- `--config`：配置文件路径

### 作为独立脚本运行

要作为独立脚本运行转换器：

```bash
python stl_to_glb_converter.py --input "输入目录" --output "输出目录"
```

### 作为服务运行

要安装并作为服务运行：

```bash
python run_as_service.py --input "输入目录" --output "输出目录"
```

这将安装转换器作为系统服务，随系统自动启动。

## 配置

转换器可以使用JSON配置文件进行配置。默认配置：

```json
{
  "input_directory": "input",
  "output_directory": "output",
  "backup_directory": "backup",
  "log_file": "stl_to_glb.log",
  "console_log_level": "INFO",
  "file_log_level": "DEBUG",
  "recursive_scan": false,
  "watch_interval": 1.0,
  "auto_clean": false,
  "parallel_processing": true,
  "max_workers": null,
  "export_options": {
    "smooth": true,
    "include_normals": true,
    "include_texture": true
  }
}
```

## 工作原理

1. 系统启动时处理输入目录中已有的STL文件
2. 然后持续监控输入目录中新增或修改的STL文件
3. 当检测到新的STL文件时，自动将其转换为GLB格式
4. 转换后的GLB文件保存到输出目录
5. 所有转换活动都记录到控制台和日志文件中

## 故障排除

- 检查日志文件（`stl_to_glb.log`、`batch_convert.log`或`stl_to_glb_service.log`）中的错误信息
- 确保对输入和输出目录有适当的权限
- 对于服务安装问题，检查系统特定的服务管理工具
- 使用更高的日志级别获取更详细的信息

## 许可证

本项目是开源的，遵循MIT许可证。

## 贡献

欢迎贡献！请随时提交Pull Request。 