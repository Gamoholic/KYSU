#!/usr/bin/env python
import datetime, os, re, sys, urllib

# Global Variables
FH = 'http://www.filehippo.com'
EXTS = ['.exe', '.msi', '.iso', '.zip']
ARGS = sys.argv[1:]
arg_dict = {'test': '-test', 'url': '-url', 'final': '-final'}
op_dict = {'test': False, 'url': False, 'final': False}
if not ARGS:
    print 'usage: [-test] [-url] [-final] db_file download_location'
    sys.exit(1)
del_args = 0
for arg in range(len(ARGS)):
    for key in arg_dict:
        if ARGS[arg] == arg_dict[key]:
            op_dict[key] = True
            del_args += 1
TEST = op_dict['test']
URL = op_dict['url']
FINAL = op_dict['final']
for val in range(del_args):
    del ARGS[0]
    
def make_html(url): 
    html = urllib.urlopen(url).read()
    if re.search('404 \- Not Found', html) != None:
        print '{} {} {}'.format(cur_time(), "Bad URL:", url)
    return html
  
def name_gen(name, ver):
    if name.endswith('/') or name.find('$') == -1: 
        final_name = name
    else: 
        final_name = name_replace(name, ver)
        counter_abortion = 0
        while '$' in final_name: 
            counter_abortion += 1
            final_name = name_replace(final_name, ver)
            if counter_abortion == 5:
                final_name = "BROKEN"
                break
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
    dict_a = {}
    files = [s for s in filenames for x in EXTS if s.endswith(x)]
    for s in files:
        dict_a[res('(.*)\-', s, 1)] = res('-([\d\.]*)\.\w+', s, 1)
    return dict_a

def res(regex, string, x):
    a = re.search(regex, string)
    try: 
        return a.group() if x == 0 else a.group(x)
    except AttributeError: 
        return ''
        
def cur_time():
    return datetime.datetime.now().strftime("%H:%M:%S")
        
#Main
print datetime.datetime.now().strftime("%m-%d-%Y") #Today's date
local_files = os.listdir(ARGS[1])
big_list = [s.split() for s in open(ARGS[0], 'rU').readlines()
    if not s.startswith('#')]
final_list, url_list, final_dict, url_dict = [], [], {}, {}
for alist in big_list: 
    name = res('(.*)\-', alist[0], 1)
    ver = res(alist[3], make_html(alist[1]), 0)
    if ver == '':
        print '{} {} {}'.format(cur_time(), "Unable to find version number for:", name)
    else:
        url = name_gen(alist[2], ver)
        final = name_gen(alist[0], ver)
        if url != "BROKEN" and final != "BROKEN":
            url_list.append(url)
            final_list.append(final)
            url_dict[name] = url
            final_dict[name] = final
            if URL == True: 
                print '{} {} {}'.format(cur_time(), name, url)
            if FINAL == True: 
                print '{} {}'.format(cur_time(), final)
        else:
            print '{} {} {}'.format(cur_time(), "Skipped due to improper use of $:", name)
local_dict = build_dict(local_files)
update_dict = build_dict(final_list)
counter_updated, counter_new = 0,0
for key in update_dict:
    down_loc = ARGS[1] + final_dict[key]
    if key in local_dict:
        if local_dict[key] != update_dict[key]:
            counter_updated += 1
            del_var = key + '-' + local_dict[key]
            for s in local_files:
                if s.find(del_var) != -1:
                    print '{} {} {}'.format(cur_time(), 'Deleted', s)
                    if TEST == False:
                        os.remove(ARGS[1] + s)
            print '{} {} {}'.format(cur_time(), 'Downloading', 
                final_dict[key])
            if TEST == False:
                urllib.urlretrieve(url_dict[key], down_loc)
    else:
        counter_new += 1
        print '{} {} {}'.format(cur_time(), 'Downloading', 
            final_dict[key])
        if TEST == False:
            urllib.urlretrieve(url_dict[key], down_loc)
if counter_updated == 1: 
    print '{} {}'.format(cur_time(), '1 file updated.')
else: 
    print '{} {} {}'.format(cur_time(), counter_updated, 'files updated.')
if counter_new == 1: 
    print '{} {}'.format(cur_time(), '1 new file.')
else: 
    print '{} {} {}'.format(cur_time(), counter_new, 'new files.')
print
