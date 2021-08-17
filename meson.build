project('frog',
          version: '0.1.0',
    meson_version: '>= 0.50.0',
  default_options: [ 'warning_level=2',
                   ],
)

author = 'tenderowl'
domain = 'com.github'
# app_id built as: domain.author.project_name
gitrepo = 'https://github.com/'+author+'/'+meson.project_name()
website = 'https://tenderowl.com'


i18n = import('i18n')
python = import('python3')
gnome = import('gnome')
prefix = get_option('prefix') # should be /usr
bindir = get_option('bindir') # should be bin
datadir = get_option('datadir') # should be /usr/share
pkgdatadir = join_paths(prefix, datadir, meson.project_name())
pythondir = join_paths(prefix, python.sysconfig_path('purelib'))
localedir = join_paths(prefix, get_option('localedir'))


install_subdir('frog', install_dir: pythondir)
subdir('bin')
subdir('data')
subdir('po')

meson.add_install_script('build-aux/meson/postinstall.py')
