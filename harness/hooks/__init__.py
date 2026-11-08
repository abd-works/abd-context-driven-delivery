"""Hooks: the ``@hook`` annotation, the hook server and daemon that run hooked operations, and the hook channel of an
install. Importing the package registers the hook channel's installation with the Installer, so any process that uses
hooks installs them too."""
import harness.hooks.hook_installation  # noqa: F401
