import re
import subprocess as sp
import json
import hashlib
import urllib.request
import os.path
import argparse

if os.name == 'nt':
    # Windows, parse args.
    parser = argparse.ArgumentParser(description='Packwiz Helper')
    parser.add_argument('--nodep', action='store_true', dest='dep',help='Don\'t auto install dependencies.')
    args = parser.parse_args()
    if args.dep:
        dep = 'n'
    else:
        dep = 'y'
    #Download latest version of packwiz.
    print('Downloading latest version of Packwiz...')
    sp.run(['curl.exe', '-L', 'https://nightly.link/packwiz/packwiz/workflows/go/master/Windows%2064-bit.zip', '-o', 'update.zip', '-k'], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    sp.run(['powershell.exe', '-c', 'Expand-Archive','update.zip', '-DestinationPath', '.', '-Force'], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    os.remove('update.zip')
    sp.call(['packwiz.exe', 'init'])
    #Import mods from text file.
    with open('pack.toml') as file:
        if 'no-internal-hashes' in file.read():
            #Reject if pack.toml has no-internal-hashes.
            print('pack.toml has no-internal-hashes.')
        else:
            #Make sure hashing for files is disabled.
            with open('pack.toml', 'a') as file:
                file.write('\n[options]\nno-internal-hashes = "true"')
    #Main script.
    value = input('Welcome to BetaTester41\'s Packwiz Maker! Please select from the following options:\n1. Import mods from text file. (Curseforge, Modrinth, GitHub Releases)\n2. Add custom mods using custom URL. (Auto Update not supported!)\n3. Generate for distribution\n4. Update All\n5. Exit\nChoice: ')
    while not value.isnumeric() or int(value) > 5:
        #Reject invalid input.
        value = input('Not Valid! Try Again: ')
    if int(value) == 1:
        with open('mods.txt', 'r') as file:
            for line in file:
                curse = re.compile('\d{6}')
                modrth = re.compile('[a-zA-Z\d]+')
                git = re.compile('.*\/.*[^\/]')
                #act = re.compile('.*\/.*\/.*[^\/]')
                clean = line.strip();
                if curse.match(clean):
                    id = curse.match(clean).group()
                    process = sp.run(['echo', dep, '|', 'packwiz.exe', 'cf', 'install', id], shell=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
                    if process.returncode != 0:
                        print('\033[31m', 'Mod ID:', id, 'failed to install! The mod may be unavailable or incompatible. Curseforge', '\033[0m')
                    else:
                        print('\033[32m', 'Mod ID:', id, 'installed successfully!', '\033[0m')
                elif modrth.match(clean) and not git.match(clean):
                    id = modrth.match(clean).group()
                    process = sp.run(['echo', dep, '|', 'packwiz.exe', 'mr', 'install', id], shell=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
                    if process.returncode != 0:
                        print('\033[31m', 'Mod ID:', id, 'failed to install! The mod may be unavailable or incompatible. Modrinth', '\033[0m')
                    else:
                        print('\033[32m', 'Mod ID:', id, 'installed successfully!', '\033[0m')
                elif git.match(clean):
                    github = urllib.request.urlopen('https://api.github.com/repos/{}/releases/latest'.format(git.match(clean).group()))
                    data = json.loads(github.read().decode(github.info().get_param('charset') or 'utf-8'))
                    i = 0
                    question = []
                    name = []
                    print('')
                    for asset in data['assets']:
                        question.append(data['assets'][i]['browser_download_url'])
                        name.append(data['assets'][i]['name'])
                        print(str(i+1) + '.', data['assets'][i]['browser_download_url'])
                        i = i+1
                    while True:
                        try:
                            index = int(input('Choose one from above: '))-1
                            if index <= len(question)-1 and index > -1:
                                break
                            else:
                                print('Not an option!')
                        except:
                            continue
                    sp.run(['curl.exe', '-L', question[index], '-o', 'tmp.jar', '-k'], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
                    final = 'name = "{name}"\nfilename = "{file}"\nside = "client"\n\n[download]\nurl = "{url}"\nhash-format = "sha512"\nhash = "{hash}"'.format(name=str.title(git.match(clean).group().split('/')[1].replace('_', ' ').replace('-', ' ')), file=name[index], url=question[index], hash=hashlib.sha512(open('tmp.jar', 'rb').read()).hexdigest())
                    if not os.path.isdir('mods'):
                        os.mkdir('mods')
                    with open('mods/'+ git.match(clean).group().split('/')[1].replace('_', '-') + '.toml', 'w') as new:
                        new.write(final)
                    sp.run(['packwiz.exe', 'refresh'], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        #os.remove('packwiz.exe')
    elif int(value) == 2:
        modurl = input('Please enter the URL of the mod: ')
        modname = input('Name of Mod: ')
        sp.run(['curl.exe', '-L', modurl, '-o', 'tmp.jar', '-k'], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        final = 'name = "{name}"\nfilename = "{file}"\nside = "client"\n\n[download]\nurl = "{url}"\nhash-format = "sha512"\nhash = "{hash}"'.format(name=str.title(modname), file=os.path.basename(modurl), url=modurl, hash=hashlib.sha512(open('tmp.jar', 'rb').read()).hexdigest())
        if not os.path.isdir('mods'):
            os.mkdir('mods')
        with open('mods/'+ modname.replace(' ', '-') + '.toml', 'w') as new:
            new.write(final)
        sp.run(['packwiz.exe', 'refresh'], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        os.remove('tmp.jar')
    elif int(value) == 3:
        sp.run(['packwiz.exe', 'refresh', '--build'], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        print('\033[32m', 'Build Successful!', '\033[0m')
    elif int(value) == 4:
        sp.run(['packwiz.exe', 'update', '-a'], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    elif int(value) == 5:
        exit(0)
    else:
        print('That\'s not supposed to happen!')
        exit(1)
else:
    print('This script is only for Windows, Exiting...')
