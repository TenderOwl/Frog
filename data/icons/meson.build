application_id = 'com.github.tenderowl.frog'

icon_sizes = ['32', '48', '64', '128']

icons_dir = join_paths(get_option('datadir'), 'icons', 'hicolor')
foreach size : icon_sizes
	asset = join_paths('@0@x@0@'.format(size), '@0@.svg'.format(application_id))
	install_data(
			asset,
			install_dir:  join_paths(icons_dir, '@0@x@0@'.format(size), 'apps'),
			rename: '@0@.svg'.format(application_id)
	)
	install_data(
			asset,
			install_dir: join_paths(icons_dir,  '@0@x@0@@2'.format(size), 'apps'),
			rename: '@0@.svg'.format(application_id)
	)
endforeach

scalable_dir = join_paths('hicolor', '128x128',  '@0@.svg'.format(application_id))
install_data(
  join_paths( '128x128', ('@0@.svg').format(application_id)),
  install_dir: join_paths(get_option('datadir'), 'icons', scalable_dir)
)

