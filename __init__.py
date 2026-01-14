"""
Jackify - A tool for running Wabbajack modlists on Linux

This package provides both CLI and GUI interfaces for managing
Wabbajack modlists natively on Linux systems.
"""

__version__ = "0.2.1"


def main():
    """Main entry point - launch GUI by default"""
    from frontends.gui.main import main as gui_main
    return gui_main()
