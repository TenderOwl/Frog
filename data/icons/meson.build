application_id = '.'.join([domain, author, meson.project_name()])

install_data(
  '@0@.svg'.format(application_id),
  install_dir: join_paths(get_option('datadir'), 'icons', 'hicolor', 'scalable', 'apps')
)

install_data(
  '@0@-symbolic.svg'.format(application_id),
  install_dir: join_paths(get_option('datadir'), 'icons', 'hicolor', 'symbolic', 'apps')
)
