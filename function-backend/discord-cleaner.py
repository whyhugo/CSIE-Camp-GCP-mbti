import re
from datetime import datetime

raw_text = """
"""  # ← 這裡貼上原始複製的 Discord 對話

lines = raw_text.strip().split("\n")

output = []
i = 0
while i < len(lines):
    match = re.match(r"(.+?)\s+—\s+(\d+/\d+/\d+ \d+:\d+ [AP]M)", lines[i])
    if match:
        name = match.group(1)
        timestamp = datetime.strptime(match.group(2), "%m/%d/%Y %I:%M %p")
        time_str = timestamp.strftime("%H:%M")
        i += 1
        if i < len(lines):  # 避免越界
            message = lines[i].strip()
            output.append(f"{time_str} {name} {message}")
    i += 1

# 印出或儲存結果
for line in output:
    print(line)
