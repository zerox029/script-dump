import re

read_location = ""
write_location = ""

f = open(read_location, "r", encoding="utf8")

content = f.read()
content_list = content.splitlines()

content_list = list(filter(None, content_list))  # Removing empty elements
del content_list[1::2]  # Removing english definitions
content_list = [re.sub(r'\（[^)]*\）', '', word) for word in content_list] # Remove furigana

# Writing to a file
with open(write_location, 'w') as f:
    for word in content_list:
        f.write("%s\n" % word)