# -*- coding: utf-8 -*-
"""
Dev server launcher - Compatibility layer.

This file now redirects to backend.launcher.server_launcher.
Please update your imports to use the new module path.
"""

from backend.launcher.server_launcher import main

if __name__ == "__main__":
    main()
