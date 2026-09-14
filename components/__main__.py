"""`python -m components ...` is the same as the `components` console script."""
import sys

from .cli import main

sys.exit(main())
