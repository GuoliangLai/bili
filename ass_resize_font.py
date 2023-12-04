input_file = 'tmp/Adult.m3u'
output_file = 'tmp/Adult_out.m3u'

with open(input_file, 'r', encoding='utf-8') as file:
    lines = file.readlines()

output_lines = []
for line in lines:
    if line.startswith('#EXTINF:'):
        parts = line.split('group-title="')[1].split('"')
        title = parts[1].split(',')[1].replace('\n', '')
    elif line.startswith('http'):
        url = line.strip()
        output_lines.append(f'{title},{url}\n')

with open(output_file, 'w', encoding='utf-8') as file:
    file.writelines(output_lines)
