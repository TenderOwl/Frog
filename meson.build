project('frog',
          version: '1.5.0',
    meson_version: '>= 0.50.0',
  default_options: [ 'warning_level=2',
                   ],
)

author = 'tenderowl'
domain = 'com.github'
# app_id built as: domain.author.project_name
gitrepo = 'https://github.com/'+author+'/'+meson.project_name()
website = 'https://getfrog.app'


i18n = import('i18n')
# see https://mesonbuild.com/Release-notes-for-0-48-0.html#python3-module-is-deprecated
pymod = import('python')
python = pymod.find_installation()
gnome = import('gnome')
prefix = get_option('prefix') # should be /usr
bindir = get_option('bindir') # should be bin
datadir = get_option('datadir') # should be /usr/share
pkgdatadir = join_paths(prefix, datadir, meson.project_name())
pythondir = python.get_install_dir()
localedir = join_paths(prefix, get_option('localedir'))


install_subdir('frog', install_dir: pythondir)
subdir('bin')
subdir('data')
subdir('po')

meson.add_install_script('build-aux/meson/postinstall.py')
