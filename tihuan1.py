import os
import re
import logging

# 设置日志配置
logging.basicConfig(
    filename='file_replace.log',  # 日志文件名
    level=logging.INFO,           # 日志级别
    format='%(asctime)s - %(levelname)s - %(message)s',  # 日志格式
    datefmt='%Y-%m-%d %H:%M:%S'    # 日期格式
)

def replace_header_in_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 使用正则查找 <!-- Start Header Area --> 和 <!-- End Header Area --> 之间的内容
        header_area_pattern = r'<!-- Start Footer Area -->.*?<!-- End Footer Area -->'
        new_content = re.sub(header_area_pattern, '{% include "/footer.html" %}', content, flags=re.DOTALL)

        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        # 记录日志：文件处理成功
        logging.info(f"Successfully processed: {file_path}")
    except Exception as e:
        # 记录日志：处理文件时出错
        logging.error(f"Error processing {file_path}: {e}")

def process_templates_directory(directory_path):
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            # 检查文件是否为 HTML 文件且不包含 'zh'
            if file.endswith('.html') and 'zh' not in file:
                file_path = os.path.join(root, file)
                logging.info(f"Processing file: {file_path}")
                replace_header_in_file(file_path)

if __name__ == '__main__':
    templates_directory = 'templates'  # 你的 templates 目录路径
    logging.info("Script started.")
    process_templates_directory(templates_directory)
    logging.info("Finished processing all files.")
