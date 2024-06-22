"""
This configuration file for pytest ensures that the `src` directory is added to the Python path.

By adding the `src` directory to `sys.path`, we can ensure that modules within `src` can be
imported easily during testing, regardless of the current working directory.

This approach helps in resolving import errors when running tests with pytest.
"""

import sys
import os

# Add the src directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
