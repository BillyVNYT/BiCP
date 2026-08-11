# Changelog

## [1.1.0]

### Added

- Settings window
- Persistent settings
- Language preference persistence
- Editor font and tab-size settings
- C++ compiler settings
- Python interpreter setting
- Editable default C++ and Python templates

### Improved

- Runtime settings now configure the editor, compiler, runner, and workspace templates.
- README and release documentation now describe the settings release.

### Fixed

- Settings Apply now updates runtime behavior instead of only closing the dialog.
- Save and Save As shortcuts are separated to avoid ambiguous `Ctrl+S` behavior.

## [1.0.0]

### Added

- Initial BiCP desktop IDE
- C++ execution
- Python execution
- Code editor with line numbers
- Input/output workflow
- Run, Rebuild, and Stop controls
- Compile error, runtime error, timeout, and exit-code reporting
- Save, Save As, and Find shortcuts
- PyInstaller build script
