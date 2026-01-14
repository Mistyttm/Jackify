#!/usr/bin/env python3
"""
Main entry point for Jackify package.
Launches the GUI by default.
"""

import sys

def main():
    """Main entry point - launch GUI by default"""
    from frontends.gui.main import main as gui_main
    return gui_main()

if __name__ == "__main__":
    main()
