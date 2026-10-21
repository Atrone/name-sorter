"""A person's name, split into given names and a last name, and the rules it must follow."""

from __future__ import annotations

from dataclasses import dataclass

MIN_GIVEN_NAMES = 1
MAX_GIVEN_NAMES = 3


class InvalidNameError(ValueError):
    """Raised when text, or the parts passed in, don't make a valid name."""


@dataclass(frozen=True)
class PersonName:
    """A person's name: one to three given names followed by a last name.

    The rules are checked when a PersonName is created, so code holding one can
    rely on it being valid without checking again. Instances are immutable, so a
    name can be shared and sorted without being changed by accident.

    Attributes:
        given_names: Given names in the order they're written, e.g. ("Adonis", "Julius").
        last_name: The family name, e.g. "Archer".
    """

    given_names: tuple[str, ...]
    last_name: str

    def __post_init__(self) -> None:
        """Check the name follows the rules, whether it was parsed or built directly.

        Raises:
            InvalidNameError: If any part isn't a single word, or there are fewer
                than one or more than three given names.
        """
        # A part containing whitespace would make full_name read back as a different name.
        for part in (*self.given_names, self.last_name):
            if not _is_single_word(part):
                raise InvalidNameError(
                    f"{part!r} is not a valid name part: each given name and the last name "
                    "must be a single word."
                )

        # A name needs at least one given name and may have at most three.
        if not MIN_GIVEN_NAMES <= len(self.given_names) <= MAX_GIVEN_NAMES:
            raise InvalidNameError(
                f"{self.full_name!r} is not a valid name: it needs {MIN_GIVEN_NAMES} to "
                f"{MAX_GIVEN_NAMES} given names followed by a last name."
            )

    @classmethod
    def parse(cls, text: str) -> PersonName:
        """Read a name written as given names followed by a last name.

        The last word is the last name and every word before it is a given name.
        Extra whitespace around or between words is ignored, so "  Leo   Gardner "
        reads the same as "Leo Gardner".

        Args:
            text: The name as written, e.g. "Adonis Julius Archer".

        Returns:
            The parsed name.

        Raises:
            InvalidNameError: If the text is blank, or doesn't have one to three
                given names before the last name.
        """
        # With no argument, split() breaks on any run of whitespace and ignores it at both ends.
        words = text.split()

        # Blank text has no last word to take, so it gets its own check and message.
        if not words:
            raise InvalidNameError("A name cannot be blank.")

        # The last word is the last name; the constructor checks how many given names are left.
        *given_names, last_name = words
        return cls(given_names=tuple(given_names), last_name=last_name)

    @property
    def full_name(self) -> str:
        """The name as it's displayed, e.g. "Adonis Julius Archer"."""
        # Given names come first, in the order they were written, then the last name.
        return " ".join((*self.given_names, self.last_name))


def _is_single_word(text: str) -> bool:
    """Return True if the text is exactly one word, with no whitespace anywhere in it.

    Args:
        text: The text to check.

    Returns:
        True for "Archer"; False for "", " Archer" or "Mary Anne".
    """
    # split() drops outer whitespace and breaks on inner whitespace, so only a clean
    # single word comes back unchanged as a one-item list.
    return text.split() == [text]
