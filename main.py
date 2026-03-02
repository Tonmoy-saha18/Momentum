"""Momentum — Offline course learning tracker."""

import sys

from momentum.app import MomentumApp


def main():
    app = MomentumApp(sys.argv)
    sys.exit(app.run())


if __name__ == "__main__":
    main()
