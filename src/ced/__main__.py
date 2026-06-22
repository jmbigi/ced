from __future__ import annotations

from ced.app import Ced


def main() -> None:
    """Entry point: create and run the ced editor application."""
    app = Ced()
    app.run()


if __name__ == "__main__":
    main()
