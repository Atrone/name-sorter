"""Tests for PersonName: reading a name from text, and the rules every name must follow."""

from dataclasses import FrozenInstanceError

import pytest

from name_sorter.person_name import InvalidNameError, PersonName


class TestParse:
    """PersonName.parse reads text as given names followed by a last name."""

    @pytest.mark.parametrize(
        ("text", "expected_given_names", "expected_last_name"),
        [
            ("Marin Alvarez", ("Marin",), "Alvarez"),
            ("Beau Tristan Bentley", ("Beau", "Tristan"), "Bentley"),
            ("Hunter Uriah Mathew Clarke", ("Hunter", "Uriah", "Mathew"), "Clarke"),
        ],
        ids=["one given name", "two given names", "three given names"],
    )
    def test_last_word_is_the_last_name_and_earlier_words_are_given_names(
        self, text, expected_given_names, expected_last_name
    ):
        """Names with one, two or three given names are all split the same way."""
        name = PersonName.parse(text)

        # Order matters here: sorting compares given names from first to last.
        assert name.given_names == expected_given_names
        assert name.last_name == expected_last_name

    def test_ignores_extra_whitespace_around_and_between_words(self):
        """Stray spaces and tabs in the input don't end up inside the name."""
        # Leading, trailing, repeated and tab characters should all be dropped.
        name = PersonName.parse("  Leo \t  Gardner  ")

        assert name == PersonName(given_names=("Leo",), last_name="Gardner")

    def test_splits_on_whitespace_only_so_hyphens_and_apostrophes_stay_in_the_word(self):
        """Punctuation inside a word is part of the name, not a separator."""
        name = PersonName.parse("Mary-Jane O'Brien")

        # "Mary-Jane" is one given name and "O'Brien" is one last name.
        assert name == PersonName(given_names=("Mary-Jane",), last_name="O'Brien")

    @pytest.mark.parametrize("text", ["", "   ", "\t"], ids=["empty", "spaces", "tab"])
    def test_rejects_blank_text(self, text):
        """Text with no words in it isn't a name."""
        # There's no last name to take, so parsing fails instead of guessing.
        with pytest.raises(InvalidNameError, match="cannot be blank"):
            PersonName.parse(text)

    def test_rejects_a_single_word_because_it_has_no_given_name(self):
        """A lone word is a last name with no given name, which isn't allowed."""
        # The message states the rule, so whoever wrote the file knows how to fix it.
        with pytest.raises(InvalidNameError, match="1 to 3 given names"):
            PersonName.parse("Madonna")

    def test_rejects_more_than_three_given_names(self):
        """Four given names is one more than a name may have."""
        # The extra given name must be reported, not silently dropped.
        with pytest.raises(InvalidNameError, match="1 to 3 given names"):
            PersonName.parse("Hunter Uriah Mathew James Clarke")


class TestFullName:
    """full_name is the form a name is printed and saved in."""

    def test_joins_given_names_and_last_name_with_single_spaces(self):
        """Given names come first, in order, followed by the last name."""
        name = PersonName(given_names=("Adonis", "Julius"), last_name="Archer")

        # This is the exact text that appears on screen and in the output file.
        assert name.full_name == "Adonis Julius Archer"

    def test_parsing_the_full_name_gives_back_the_same_name(self):
        """Writing a name out and reading it back in doesn't change it."""
        name = PersonName(given_names=("Hunter", "Uriah", "Mathew"), last_name="Clarke")

        # A sorted output file can be fed back in as input, so the round trip must be lossless.
        assert PersonName.parse(name.full_name) == name


class TestDirectConstruction:
    """The rules also apply when a PersonName is created directly instead of parsed."""

    @pytest.mark.parametrize(
        "given_names",
        [(), ("Hunter", "Uriah", "Mathew", "James")],
        ids=["no given names", "four given names"],
    )
    def test_rejects_fewer_than_one_or_more_than_three_given_names(self, given_names):
        """The given-name limits can't be bypassed by skipping parse."""
        # Both ends of the allowed range are checked: zero is too few and four is too many.
        with pytest.raises(InvalidNameError, match="1 to 3 given names"):
            PersonName(given_names=given_names, last_name="Clarke")

    @pytest.mark.parametrize(
        ("given_names", "last_name"),
        [
            (("",), "Clarke"),
            (("Mary Anne",), "Clarke"),
            (("Leo",), ""),
            (("Leo",), " Gardner"),
        ],
        ids=[
            "empty given name",
            "given name containing a space",
            "empty last name",
            "last name with a leading space",
        ],
    )
    def test_rejects_parts_that_are_not_a_single_word(self, given_names, last_name):
        """Every part must be one word, or full_name would read back as a different name."""
        # For example, "Mary Anne Clarke" would parse as two given names instead of one.
        with pytest.raises(InvalidNameError, match="single word"):
            PersonName(given_names=given_names, last_name=last_name)

    def test_cannot_be_changed_after_creation(self):
        """Names are immutable, so sorting or sharing one can't alter it."""
        name = PersonName.parse("Leo Gardner")

        # Frozen dataclasses raise an error on any attempt to reassign a field.
        with pytest.raises(FrozenInstanceError):
            name.last_name = "Lewis"
