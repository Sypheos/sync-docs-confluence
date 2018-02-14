import os
import sys
import json
import requests
from bs4 import BeautifulSoup

DOMAIN= "<domain>"
BASE_URL= "https://{domain}.atlassian.net/wiki/rest/api/".format(domain=DOMAIN)
USERNAME= "<username>"
PASSWORD= "<password>"
AUTH= (USERNAME, PASSWORD)

def get_page_info(auth, title):
    url = '{base}content?title={title}'.format(base=BASE_URL, title=title)
    r =requests.get(url, auth=auth)
    r.raise_for_status()
    return r.json()

def delete_page(auth, title):
    info = get_page_info(auth, title)
    ID = info['results'][0]['id']
    url = '{base}content/{ID}'.format(base=BASE_URL, ID=ID)
    r = requests.delete(url, auth=auth)
    r.raise_for_status()
    print("Deleted "+title)

def write_data(auth, html, title, parent=""):
    if parent:
        info = get_page_info(auth, parent)
        parentId = info['results'][0]['id']
        data = {
            'space': {
                'key': 'TTIHEROES'
            },
            'type': 'page',
            'version': {
                'number': 0
            },
            'title': title,
            'ancestors':[
                {
                    'id': str(parentId)
                }
            ],
            'body': {
                'storage':
                {
                    'representation': 'storage',
                    'value': str(html),
                }
            }
        }
    else:
        data = {
            'space': {
                'key': 'TTIHEROES'
            },
            'type': 'page',
            'title': title,
            'version': {
                'number': 0
            },
            'body': {
                'storage':
                {
                    'representation': 'storage',
                    'value': str(html),
                }
            }
        }

    data = json.dumps(data)
    url = '{base}content'.format(base=BASE_URL)
    r = requests.post(url, data=data, auth=AUTH, headers = { 'Content-Type' : 'application/json' })
    r.raise_for_status()
    print("Created "+title)

def iterateThroughDir():
    for subdir, dirs, files in os.walk("."):
        name = selectLastDir(subdir)
        if(name.find(".")<0):
            if(sys.argv[1]=="delete"):
                delete_page(AUTH, name)
            else:
                parentpath = removeLastDirFromFilepath(subdir)
                if(parentpath!="./"):
                    parentpath =replaceBetween(len(parentpath)-1, len(parentpath), parentpath, "")
                    parent = selectLastDir(parentpath)
                    write_data(AUTH, "<p>Section relatives to "+name+".</p>", name, parent)
                else:
                    write_data(AUTH, "<p>Section relatives to "+name+".</p>", name, "Documentation")

        for file in files:
            sub_dir = selectLastDir(subdir)
            filepath = subdir + os.sep + file
            filename = selectLastDir(filepath)

            if filepath.endswith(".md"):
                filename = replaceBetween(len(filename)-3,len(filename), filename, "")
                if(sys.argv[1]=="delete"):
                    delete_page(AUTH, filename+" - "+sub_dir)
                else:
                    filePath = removeLastDirFromFilepath(filepath)
                    filePath = replaceBetween(0, 1, filePath, "")
                    htmlpath = replaceBetween(len(filepath)-3, len(filepath), filepath, ".html")
                    os.system("pandoc {fp} -f markdown -t html -o {htmlfile}".format(fp=filepath, htmlfile=htmlpath))
                    with open(htmlpath, 'r') as fd:
                        html = fd.read()
                        html = prepare_html(html, filePath)
                        write_data(AUTH, html, filename+" - "+sub_dir, sub_dir)
                        os.system("rm {htmlfile}".format(htmlfile=htmlpath))

def replaceBetween(startIndex, endIndex, oldStr, replacement):
    string = oldStr[0:startIndex] + replacement + oldStr[endIndex+1:]
    return string

def removeLastDirFromFilepath(filepath):
    i=0
    if(filepath.endswith("/") and len(filepath)>1):
        filepath = replaceBetween(len(filepath)-1, len(filepath), filepath, "")
    while(i<len(filepath)):
        res = filepath.find("/", i)
        if res < 0 :
            break
        else:
            i = res + 1
    if i == len(filepath):
        return ""
    else:
        withoutLastDir = replaceBetween(i, len(filepath), filepath, "")
        return withoutLastDir

def selectLastDir(filepath):
    i=0
    while i<len(filepath):
        res = filepath.find("/", i)
        if res < 0:
            return filepath
        else:
            filepath = replaceBetween(0, res, filepath, "")


def prepare_html(html, filepath):
    soup = BeautifulSoup(html, "html.parser")
    img_tags = soup.findAll('img')
    sources = []
    i = 0
    if(img_tags):
        while len(sources) < len(img_tags):
            src = soup.findAll('img')[i]['src']
            sources.append(src)
            i = i+1

        for src in sources:
            sources.remove(src)
            relpath = src.find('../')
            if (relpath >= 0):
                doublerelpath = src.find('../../')
                if(doublerelpath>=0):
                    fin = 5
                    src = replaceBetween(0, fin, src, "https://www.thethingsnetwork.org/docs/" +removeLastDirFromFilepath(removeLastDirFromFilepath(filepath)))
                else:
                    fin = 2
                    src = replaceBetween(0, fin, src, "https://www.thethingsnetwork.org/docs/" + removeLastDirFromFilepath(filepath))
            else:
                src = "https://www.thethingsnetwork.org/docs/" + filepath + src
            sources.insert(0, src)
        count = len(sources)
        while(i<len(html)):
            debut_img = html.find("<img", i)
            if(debut_img>=0):
                i = debut_img
                fin_img = html.find("/>", i)
                html = replaceBetween(i, fin_img+1, html, '<ac:image ac:height="250"><ri:url ri:value="' + sources[count-1] + '"/></ac:image>')
                count = count - 1
                i = fin_img + 1
            else:
                break
    return html

iterateThroughDir()
