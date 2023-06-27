app_id = '.'.join([
    domain,
    author,
    meson.project_name()
])

desktop_file = i18n.merge_file(
  input: 'com.github.tenderowl.frog.desktop.in',
  output: 'com.github.tenderowl.frog.desktop',
  type: 'desktop',
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'applications')
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils,
    args: [desktop_file]
  )
endif

appstream_file = i18n.merge_file(
  input: 'com.github.tenderowl.frog.appdata.xml.in',
  output: 'com.github.tenderowl.frog.appdata.xml',
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'appdata')
)

appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
  test('Validate appstream file', appstream_util,
    args: ['validate', appstream_file]
  )
endif

install_data('com.github.tenderowl.frog.gschema.xml',
  install_dir: join_paths(get_option('datadir'), 'glib-2.0/schemas')
)

# Default tesseract trained model
install_data('tessdata/eng.traineddata',
  install_dir: join_paths(get_option('datadir'), 'appdata')
)

compile_schemas = find_program('glib-compile-schemas', required: false)
if compile_schemas.found()
  test('Validate schema file', compile_schemas,
    args: ['--strict', '--dry-run', meson.current_source_dir()]
  )
endif

subdir('icons')

blueprints = custom_target('blueprints',
  input: files(
    'ui/language_dialog.blp',
    'ui/preferences_dialog.blp',
    'ui/preferences_general.blp',
    'ui/preferences_languages.blp',
    'ui/shortcuts.blp',
    'ui/window.blp',
    'ui/language_popover.blp',
    'ui/language_row.blp',
    'ui/welcome_page.blp',
    'ui/extracted_page.blp',
  ),
  output: '.',
  command: [find_program('blueprint-compiler'), 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)

app_resources = gnome.compile_resources(app_id,
    app_id + '.gresource.xml',
    gresource_bundle: true,
    dependencies: blueprints,
    install: true,
    install_dir: pkgdatadir
)

