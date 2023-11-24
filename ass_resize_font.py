import re

def modify_ass_subtitle_size(ass_file, new_size):
    # 读取 ASS 文件
    with open(ass_file, 'r', encoding='utf-8') as file:
        content = file.readlines()

    # 查找字幕大小所在的行索引
    size_index = -1
    for i, line in enumerate(content):
        if line.startswith('Style:'):
            size_index = i
            break

    # 如果找到字幕大小所在的行
    if size_index != -1:
        # 将该行按逗号分割为字段列表
        fields = content[size_index].split(',')
        print(fields)

        # 修改字幕大小字段
        fields[2] = str(new_size)

        # 将修改后的字段列表重新组合为字符串
        modified_line = ','.join(fields)

        # 替换原始行内容
        content[size_index] = modified_line

        # 将修改后的内容写回到 ASS 文件
        with open(ass_file, 'w', encoding='utf-8') as file:
            file.writelines(content)

# 示例 ASS 文件路径
ass_file = r'D:\emby\b\美食作家王刚R\2023-11-21厨师长教你：“盘龙黄鳝”的家常做法，麻辣干香，回味悠长\2023-11-21厨师长教你：“盘龙黄鳝”的家常做法，麻辣干香，回味悠长.ass'

# 修改后的字幕大小
new_size = 35

# 修改 ASS 文件中的字幕大小
modify_ass_subtitle_size(ass_file, new_size)
