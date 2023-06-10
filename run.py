import requests
from urllib.parse import urlparse
import re
import subprocess
import os

def fix_url_format(target):
    parsed_target = urlparse(target)

    if not parsed_target.scheme:
        target = 'http://' + target  # prepend 'http://' if no scheme provided
        parsed_target = urlparse(target) 

    stripped_target = parsed_target.netloc.split(':')[0]  # remove port if any
    stripped_target = stripped_target.split('.')[-2:]  # remove subdomains, if any
    stripped_target = '.'.join(stripped_target)  # join it back
    if stripped_target.startswith('www.'):
        stripped_target = stripped_target[4:]  # remove 'www.' if present
    return stripped_target

def webarchive(target):
    webarchive = f"https://web.archive.org/cdx/search/cdx?url=*.{target}&output=xml&fl=original&collapse=urlkey"
    response = requests.get(webarchive)
    if response.status_code == 200:
        filename = target + ".txt"
        with open(filename, 'w') as file:
            file.write(response.text)
        print("URL Results saved to", filename)
    else:
        print("Error occurred while making the request.")

def extract_subdomains(target, stripped_target):
    subdomains = set()
    pattern = r"https?://([^/]+\.[^/]+)"
    
    crawled_file = f"{stripped_target}.txt"
    with open(crawled_file, "r") as file:
        for line in file:
            matches = re.findall(pattern, line)
            subdomains.update(matches)
            
    parsed_url = urlparse(target)
   
    filename = "subdomains_" + stripped_target + ".txt"
    with open(filename, 'w') as file:
        for subdomain in subdomains:
            if stripped_target in subdomain and subdomain.strip():
                file.write(subdomain + "\n")
                
    print("Subdomain Results saved to", filename)
    return subdomains

def delete_files_with_target_string(stripped_target):
    files_in_directory = os.listdir()
    
    for file_name in files_in_directory:
        if stripped_target in file_name and file_name.endswith(".txt"):
            os.remove(file_name)
            print(f"Deleted file: {file_name}")

# Get User input and filter it
target = input("What is the website you are targeting?: ")
stripped_target = fix_url_format(target)

# Remove old scan files for this target
delete_files_with_target_string(stripped_target)

# Get web archive URLs
webarchive(stripped_target)

# Extract unique subdomains found from web archive
subdomains = extract_subdomains(target, stripped_target)

print("")

# Get Site Software
command = ['./httpx', '-title', '-tech-detect', '-status-code', '-silent', '-nc', '-l', f"subdomains_{stripped_target}.txt", '-o', f"sitesoftware_{stripped_target}.txt"]
subprocess.run(command)
