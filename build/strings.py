from os import system, makedirs, remove
from os.path import exists
from shutil import move, copy
from .build import files


def bld_strings(target, source, env):
    map(lambda lng: __bld_strings_lng(lng, env), env['LANGUAGES'])


def __bld_strings_lng(lng, env):
    lng_dir = env['LNG'] + lng + '/LC_MESSAGES/'
    cmd = 'msgfmt -o {lng_dir}{appname}.mo {lng_dir}{appname}.po'
    system(cmd.format(lng_dir=lng_dir, appname=env['APPNAME']))


def bld_tmpl_merge(target, source, env):
    src_files = ' '.join(files(['py'], ['feedparser', 'venv']))
    lng_dir, appname, langs = env['LNG'], env['APPNAME'], env['LANGUAGES']
    cmd_tmpl = 'xgettext -d {appname} -L python -o {appname}.pot '
    system(cmd_tmpl.format(lng_dir=lng_dir, appname=env['APPNAME']) + src_files)
    __bld_tmpl_merge(lng_dir, env['LNG_CODE'], appname)
    remove(appname + '.pot')


def __bld_tmpl_merge(lng_dir, lng, appname):
    lng_base_dir = __prepare(lng_dir, lng, appname)
    __merge(lng_base_dir, appname)
    __postprocess(lng_base_dir, appname)


def __prepare(lng_base_dir, lng, appname):
    if not exists(lng_base_dir + lng + '/LC_MESSAGES'):
        makedirs(lng_base_dir + lng + '/LC_MESSAGES')
    dst = lng_base_dir + lng + '/LC_MESSAGES/%s.pot' % appname
    copy(appname + '.pot', dst)
    lng_dir = lng_base_dir + lng + '/LC_MESSAGES/'
    if not exists(lng_dir + appname + '.po'):
        lines_to_fix = ['CHARSET/UTF-8', 'ENCODING/8bit']
        map(lambda line: __fix_line(line, lng_dir, appname), lines_to_fix)
        copy(lng_dir + appname + '.pot', lng_dir + appname + '.po')
    return lng_dir


def __fix_line(line, lng_dir, appname):
    cmd_tmpl = "sed 's/{line}/' {lng_dir}{appname}.pot > " + \
        "{lng_dir}{appname}tmp.po"
    system(cmd_tmpl.format(line=line, lng_dir=lng_dir, appname=appname))
    move(lng_dir + appname + 'tmp.po', lng_dir + appname + '.pot')


def __merge(lng_dir, appname):
    cmd_str = 'msgmerge -o {lng_dir}{appname}merge.po ' + \
        '{lng_dir}{appname}.po {lng_dir}{appname}.pot'
    system(cmd_str.format(lng_dir=lng_dir, appname=appname))
    copy(lng_dir + appname + 'merge.po', lng_dir + appname + '.po')


def __postprocess(lng_dir, appname):
    lines = open(lng_dir + appname + '.po', 'r').readlines()
    with open(lng_dir + appname + '.po', 'w') as outf:
        for line in lines:
            po_str = '"POT-Creation-Date: YEAR-MO-DA HO:MI+ZONE\\n"\n'
            outf.write(po_str if line.startswith(po_str[:20]) else line)
