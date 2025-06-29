import os
import re
from pathlib import Path

def convert_paths(html_file):
    with open(html_file, 'r+', encoding='utf-8') as f:
        content = f.read()

        # 替换 CSS
        content = re.sub(
            r'href=["\']((?:assets/)?css/[^"\']+)["\']',
            lambda m: f'href="{{{{ url_for(\'static\', filename=\'{m.group(1)}\') }}}}"',
            content
        )

        # 替换 JS
        content = re.sub(
            r'src=["\']((?:assets/)?js/[^"\']+)["\']',
            lambda m: f'src="{{{{ url_for(\'static\', filename=\'{m.group(1)}\') }}}}"',
            content
        )

        # 替换 图片
        content = re.sub(
            r'src=["\']((?:assets/)?images?/[^"\']+)["\']',
            lambda m: f'src="{{{{ url_for(\'static\', filename=\'{m.group(1)}\') }}}}"',
            content
        )

        # 替换 字体（CSS 中的 url(...)）
        content = re.sub(
            r'url\(["\']?((?:assets/)?fonts?/[^"\')]+)["\']?\)',
            lambda m: f'url("{{{{ url_for(\'static\', filename=\'{m.group(1)}\') }}}}")',
            content
        )

        f.seek(0)
        f.write(content)
        f.truncate()

# 遍历 templates 下所有 html 文件
for html_file in Path('templates').rglob('*.html'):
    print(f"Processing {html_file}...")
    convert_paths(html_file)

print("✅ 所有资源路径已成功替换为 Flask 格式！")
