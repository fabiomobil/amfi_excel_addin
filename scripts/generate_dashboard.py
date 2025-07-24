#!/usr/bin/env python3
"""Dashboard generation script"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.dashboard.generator import main

if __name__ == "__main__":
    main()