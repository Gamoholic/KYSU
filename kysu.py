#!/usr/bin/env python
import datetime, os, re, sys, urllib
FH = 'http://www.filehippo.com'
EXTS = ['.exe', '.msi', '.iso', '.zip']

def make_html(url): 
    return urllib.urlopen(url).read()
  
def name_gen(name, ver):
    if name.endswith('/') or name.find('$') == -1: 
        final_name = name
    else: 
        final_name = name_replace(name, ver)
        while '$' in final_name: 
            final_name = name_replace(final_name, ver)
    if 'filehippo' in name:
        a = res('\<a.*?(Latest Version).*?span\>', make_html(name), 0)
        b = res('href=\"(.*?)\"', a, 1)
        final_name = FH + res('url\=(.*?)\"', make_html(FH + b), 1)
    return final_name

def name_replace(name, ver):
    name_rep = res('\$[^a-zA-Z]*\$', name, 0)
    delim_ver = ver.translate(None, '_.-"')
    name_list, name_str, c = [], '', 0
    for s in range(len(name_rep)):
        if name_rep[s] == '$':
            name_list.append(delim_ver[c])
            c += 1
        else: 
            name_list.append(name_rep[s])
    for s in range(len(name_list)): 
        name_str += name_list[s]
    return name.replace(name_rep, name_str)

def build_dict(filenames):
    dict_a, files = {}, [s for s in filenames for x in EXTS if s.endswith(x)]
    for s in files:
        dict_a[res('(.*)\-', s, 1)] = res('-([\d\.]*)\.\w+', s, 1)
    return dict_a

def res(regex, string, x):
    a = re.search(regex, string)
    try: 
        return a.group() if x == 0 else a.group(x)
    except AttributeError: 
        return ''

def main():
    print datetime.datetime.now().strftime("%m-%d-%Y")
    local_files = os.listdir(sys.argv[2])
    big_list = [s.split() for s in open(sys.argv[1], 'rU').readlines()
        if not s.startswith('#')]
    final_list, url_list, final_dict, url_dict = [], [], {}, {}
    for alist in big_list: 
        ver = res(alist[3], make_html(alist[1]), 0)
        url, final = name_gen(alist[2], ver), name_gen(alist[0], ver)
        print url
        url_list.append(url)
        final_list.append(final)
        name = res('(.*)\-', final, 1)
        url_dict[name], final_dict[name] = url, final
    local_dict, update_dict = build_dict(local_files), build_dict(final_list)
    c_up, c_new = 0,0
    for key in update_dict:
        down_loc = sys.argv[2] + final_dict[key]
        if key in local_dict:
            if local_dict[key] != update_dict[key]:
                c_up += 1
                print key
                del_var = key + '-' + local_dict[key]
                for s in local_files:
                    if s.find(del_var) != -1:
                        print '  Deleted', s
                        os.remove(sys.argv[2] + s)
                print '    Downloading', final_dict[key]
                urllib.urlretrieve(url_dict[key], down_loc)
        else:
            c_new += 1
            print key 
            print '  Downloading for first time!', '\n' 
            print '    Downloading', final_dict[key]
            urllib.urlretrieve(url_dict[key], down_loc)
    print
    if c_up == 1: 
        print '1 file updated.'
    else: 
        print c_up, 'files updated.'
    if c_new == 1: 
        print '1 new file.'
    else: 
        print c_new, 'new files.'
    print '', '\n'

main()