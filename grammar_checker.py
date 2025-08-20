# -*- coding: utf-8 -*-
"""
A comprehensive, modular grammar and style checking system for Python.

This module provides a robust tool for checking grammar, style, spelling, and
more in a given text. It is designed with a modular architecture, composing
several engine classes under a main GrammarChecker class.

Author: Jules
Date: 2025-08-19
"""

import re
import logging
from dataclasses import dataclass, asdict
from typing import List, Set, Dict, Any, Optional

# Suppress verbose logging from libraries
logging.basicConfig(level=logging.WARNING)
logging.getLogger("language_tool_python").setLevel(logging.ERROR)
logging.getLogger("pyspellchecker").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)

try:
    import language_tool_python
    import spacy
    from spellchecker import SpellChecker
    from textstat import textstat
    from transformers import pipeline, set_seed
except ImportError as e:
    print(f"Error: A required library is not installed. Please run 'pip install -r requirements.txt'. Missing: {e.name}")
    exit(1)

# --- Data Structure for Issues ---

@dataclass
class Issue:
    """
    Represents a single grammar or style issue found in the text.
    """
    rule_category: str
    issue_type: str
    message: str
    suggestion: Optional[str]
    offset: int
    length: int
    context: str

    def to_dict(self) -> Dict[str, Any]:
        """Converts the dataclass to a dictionary."""
        return asdict(self)

# --- Engine Classes ---

class SpellingEngine:
    """Handles spelling and typography checks."""

    def __init__(self, personal_dictionary: Optional[Set[str]] = None):
        """
        Initializes the SpellingEngine.

        Args:
            personal_dictionary: A set of words to be ignored by the spell checker.
        """
        self.spell = SpellChecker()

        # Add common technical acronyms that are often flagged as errors
        self.spell.word_frequency.load_words(['isbn', 'iban'])

        if personal_dictionary:
            self.spell.word_frequency.load_words(personal_dictionary)

        # Regex for common formats
        self.isbn_regex = re.compile(r'\b(?:ISBN(?:-1[03])?:? )?(?=[0-9X]{10}$|(?=(?:[0-9]+[- ]){3})[- 0-9X]{13}$|97[89][0-9]{10}$|(?=(?:[0-9]+[- ]){4})[- 0-9]{17}$)(?:97[89][- ]?)?[0-9]{1,5}[- ]?[0-9]+[- ]?[0-9]+[- ]?[0-9X]\b')
        self.iban_regex = re.compile(r'\b[A-Z]{2}[0-9]{2}[A-Z0-9]{4}[0-9]{7}([A-Z0-9]?){0,16}\b')

    def check(self, text: str) -> List[Issue]:
        """
        Performs spelling and typography checks.

        Args:
            text: The input text to check.

        Returns:
            A list of Issue objects.
        """
        issues = []

        # Basic spelling check
        # Remove URLs and emails before splitting into words
        text_no_urls = re.sub(r'https?://\S+|www\.\S+', '', text)
        text_no_emails = re.sub(r'\S+@\S+', '', text_no_urls)
        words = re.findall(r'\b\w+\b', text_no_emails.lower())
        misspelled = self.spell.unknown(words)

        for word in misspelled:
            # Find all occurrences of the misspelled word
            for match in re.finditer(r'\b' + re.escape(word) + r'\b', text, re.IGNORECASE):
                issues.append(Issue(
                    rule_category="Spelling",
                    issue_type="Typo",
                    message=f"Possible spelling error: '{match.group(0)}'",
                    suggestion=self.spell.correction(word),
                    offset=match.start(),
                    length=len(match.group(0)),
                    context=self._get_context(text, match.start(), len(match.group(0)))
                ))

        # Casing check (simple sentence start capitalization)
        # Split text into sentences, preserving delimiters
        sentences = re.split(r'([.?!])\s*', text)
        offset = 0
        # Iterate over sentences and delimiters
        for i in range(0, len(sentences) - 1, 2):
            sentence = sentences[i]
            delimiter = sentences[i+1]

            # Find the first alphabetical word
            first_word_match = re.search(r'^\s*([a-zA-Z]+)', sentence)
            if first_word_match:
                word = first_word_match.group(1)
                if word.islower():
                    start_pos = offset + first_word_match.start(1)
                    issues.append(Issue(
                        rule_category="Typography",
                        issue_type="Casing",
                        message="Sentence should start with a capital letter.",
                        suggestion=word.capitalize(),
                        offset=start_pos,
                        length=len(word),
                        context=self._get_context(text, start_pos, len(word))
                    ))
            offset += len(sentence) + len(delimiter) + 1 if delimiter else len(sentence)

        return issues

    def _get_context(self, text: str, offset: int, length: int, context_len: int = 30) -> str:
        """Extracts context around an error."""
        start = max(0, offset - context_len)
        end = min(len(text), offset + length + context_len)
        return f"...{text[start:offset]}[{text[offset:offset+length]}]{text[offset+length:end]}..."


class GrammarEngine:
    """Handles grammar and punctuation checks."""

    def __init__(self, picky_mode: bool = False):
        """
        Initializes the GrammarEngine.

        Args:
            picky_mode: If True, enables more pedantic rules.
        """
        try:
            self.tool = language_tool_python.LanguageTool('en-US')
        except Exception:
            self.tool = None
            print("Warning: language-tool-python could not be initialized. Grammar checks will be skipped.")

        self.picky_mode = picky_mode
        disabled_rules = ['MORFOLOGIK_RULE_EN_US'] # Disable spellcheck from LT
        if not self.picky_mode:
            # Disable style-related rules if not in picky mode
            disabled_rules.extend(['WORDY_PHRASES', 'UPPERCASE_SENTENCE_START'])
        if self.tool:
            self.tool.disabled_rules = disabled_rules

    def check(self, text: str) -> List[Issue]:
        """
        Performs grammar and punctuation checks using language-tool.

        Args:
            text: The input text to check.

        Returns:
            A list of Issue objects.
        """
        if not self.tool:
            return []

        matches = self.tool.check(text)
        issues = []
        for match in matches:
            if not self.picky_mode and match.category in ['STYLE', 'TYPOGRAPHY', 'CASING']:
                 continue

            issues.append(Issue(
                rule_category=f"Grammar/{match.category}",
                issue_type=match.ruleId,
                message=match.message,
                suggestion=', '.join(match.replacements),
                offset=match.offset,
                length=match.errorLength,
                context=match.context
            ))
        return issues


class StyleEngine:
    """Handles style checks for conciseness, formality, and vocabulary."""

    def __init__(self, picky_mode: bool = False):
        self.picky_mode = picky_mode
        self.wordy_phrases = {
            "due to the fact that": "because",
            "in the event that": "if",
            "at this point in time": "now",
            "a number of": "several",
            "in order to": "to",
        }
        self.informal_contractions = {
            "gonna": "going to",
            "wanna": "want to",
            "ain't": "is not / are not",
        }
        self.overused_words = ["very", "really", "basically", "actually"]

    def check(self, text: str) -> List[Issue]:
        """
        Performs style checks.

        Args:
            text: The input text to check.

        Returns:
            A list of Issue objects.
        """
        issues = []
        if not self.picky_mode:
            return issues

        # Wordy phrases
        for phrase, suggestion in self.wordy_phrases.items():
            for match in re.finditer(r'\b' + re.escape(phrase) + r'\b', text, re.IGNORECASE):
                issues.append(Issue(
                    rule_category="Style/Conciseness",
                    issue_type="WordyPhrase",
                    message=f"'{match.group(0)}' is wordy.",
                    suggestion=suggestion,
                    offset=match.start(),
                    length=len(match.group(0)),
                    context=self._get_context(text, match.start(), len(match.group(0)))
                ))

        # Informal contractions
        for contraction, suggestion in self.informal_contractions.items():
            for match in re.finditer(r'\b' + re.escape(contraction) + r'\b', text, re.IGNORECASE):
                issues.append(Issue(
                    rule_category="Style/Formality",
                    issue_type="InformalContraction",
                    message=f"'{match.group(0)}' is informal.",
                    suggestion=suggestion,
                    offset=match.start(),
                    length=len(match.group(0)),
                    context=self._get_context(text, match.start(), len(match.group(0)))
                ))

        # Overused words
        for word in self.overused_words:
            for match in re.finditer(r'\b' + re.escape(word) + r'\b', text, re.IGNORECASE):
                issues.append(Issue(
                    rule_category="Style/Vocabulary",
                    issue_type="OverusedWord",
                    message=f"'{word}' is often overused. Consider a stronger alternative or removing it.",
                    suggestion=None,
                    offset=match.start(),
                    length=len(word),
                    context=self._get_context(text, match.start(), len(word))
                ))

        return issues

    def _get_context(self, text: str, offset: int, length: int, context_len: int = 30) -> str:
        """Extracts context around an error."""
        start = max(0, offset - context_len)
        end = min(len(text), offset + length + context_len)
        return f"...{text[start:offset]}[{text[offset:offset+length]}]{text[offset+length:end]}..."

class SemanticsEngine:
    """Handles semantic checks like clarity and logic."""

    def check(self, text: str) -> List[Issue]:
        """
        Performs semantic checks.

        Args:
            text: The input text to check.

        Returns:
            A list of Issue objects.
        """
        issues = []

        # Double negatives
        double_neg_pattern = re.compile(r"\b(can't|cannot|don't|doesn't|isn't|aren't|wasn't|weren't|not)\s+(hardly|scarcely|no|nothing)\b", re.IGNORECASE)
        for match in double_neg_pattern.finditer(text):
            issues.append(Issue(
                rule_category="Semantics/Logic",
                issue_type="DoubleNegative",
                message="Potential double negative detected. This can create confusion.",
                suggestion="Rephrase to use a positive construction.",
                offset=match.start(),
                length=len(match.group(0)),
                context=self._get_context(text, match.start(), len(match.group(0)))
            ))

        return issues

    def _get_context(self, text: str, offset: int, length: int, context_len: int = 30) -> str:
        """Extracts context around an error."""
        start = max(0, offset - context_len)
        end = min(len(text), offset + length + context_len)
        return f"...{text[start:offset]}[{text[offset:offset+length]}]{text[offset+length:end]}..."


# --- Main GrammarChecker Class ---

class GrammarChecker:
    """
    A comprehensive grammar and style checker.
    """
    def __init__(self, personal_dictionary: Optional[Set[str]] = None, picky_mode: bool = False):
        """
        Initializes the GrammarChecker.

        Args:
            personal_dictionary: A set of custom words to ignore during spell checking.
            picky_mode: Enables stricter style and grammar checks.
        """
        self.char_limit = 150000

        self.spelling_engine = SpellingEngine(personal_dictionary)
        self.grammar_engine = GrammarEngine(picky_mode)
        self.style_engine = StyleEngine(picky_mode)
        self.semantics_engine = SemanticsEngine()

        self._nlp = None
        self._paraphraser = None

    @property
    def nlp(self):
        if self._nlp is None:
            try:
                self._nlp = spacy.load('en_core_web_sm')
            except OSError:
                print("Warning: spaCy model 'en_core_web_sm' not found. Some features might not work.")
                print("Please run: python -m spacy download en_core_web_sm")
                self._nlp = "failed"
        return self._nlp if self._nlp != "failed" else None

    @property
    def paraphraser(self):
        if self._paraphraser is None:
            try:
                self._paraphraser = pipeline("text2text-generation", model="t5-small", tokenizer="t5-small")
                set_seed(42)
            except Exception as e:
                print(f"Warning: Could not initialize paraphrasing model. Feature will be unavailable. Error: {e}")
                self._paraphraser = "failed"
        return self._paraphraser if self._paraphraser != "failed" else None

    def check(self, text: str) -> Dict[str, Any]:
        """
        Checks a given text for grammar, style, and spelling issues.

        Args:
            text: The text to check.

        Returns:
            A dictionary containing a list of issues and the corrected text.
        """
        if len(text) > self.char_limit:
            return {
                "error": f"Input text exceeds the character limit of {self.char_limit}."
            }

        all_issues = []
        all_issues.extend(self.grammar_engine.check(text))
        all_issues.extend(self.spelling_engine.check(text))
        all_issues.extend(self.style_engine.check(text))
        all_issues.extend(self.semantics_engine.check(text))

        all_issues.sort(key=lambda issue: issue.offset)

        corrected_text = self.correct(text)

        return {
            "issues": [issue.to_dict() for issue in all_issues],
            "corrected_text": corrected_text
        }

    def correct(self, text: str) -> str:
        """
        Provides a corrected version of the text based on language_tool suggestions.

        Args:
            text: The input text.

        Returns:
            A corrected version of the text.
        """
        if self.grammar_engine.tool:
            return self.grammar_engine.tool.correct(text)
        return text

    def get_text_statistics(self, text: str) -> Dict[str, Any]:
        """
        Calculates various text statistics.

        Args:
            text: The input text.

        Returns:
            A dictionary of text statistics.
        """
        if not self.nlp:
            return {"error": "spaCy model not loaded. Cannot compute statistics."}

        doc = self.nlp(text)
        word_count = len([token for token in doc if token.is_alpha])
        return {
            "word_count": word_count,
            "sentence_count": len(list(doc.sents)),
            "average_word_length": sum(len(token.text) for token in doc if token.is_alpha) / (word_count or 1),
            "reading_time_minutes": textstat.reading_time(text, ms_per_char=14.69) / 60,
            "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
            "readability_score": textstat.flesch_reading_ease(text),
        }

    def paraphrase(self, sentence: str, max_length: int = 60) -> List[str]:
        """
        Generates paraphrasing suggestions for a sentence.

        Note: The base 't5-small' model is not fine-tuned for paraphrasing and may
        default to translation (e.g., to German). For true paraphrasing, a
        model fine-tuned on a paraphrasing dataset would be required.

        Args:
            sentence: The sentence to paraphrase.
            max_length: The maximum length of the generated paraphrase.

        Returns:
            A list of paraphrased sentences.
        """
        if not self.paraphraser:
            return ["Paraphrasing model is not available."]

        text_to_paraphrase = sentence
        outputs = self.paraphraser(
            text_to_paraphrase,
            max_length=max_length,
            num_return_sequences=3,
            num_beams=5,
            early_stopping=True
        )
        return [out['generated_text'] for out in outputs]

# --- Demonstration ---

if __name__ == "__main__":
    sample_text = (
        "helo world. i am a programer. their is many issues in this text."
        "The group of student is working on there project. we wanna finish it quick."
        "Due to the fact that we are very tired, we cant hardly continue."
        "This sentance has a speeling mistake. and this one starts with a lowercase letter."
        "My IBAN is DE89370400440532013000 and the book's ISBN is 978-3-16-148410-0."
        "Its a beautiful day, isnt it?"
    )

    print("--- Initializing Grammar Checker ---")
    custom_words = {"programer", "sentance"} # Whitelist 'programer' and 'sentance'
    checker = GrammarChecker(personal_dictionary=custom_words, picky_mode=True)

    print("\n--- Checking Text ---")
    print(f"Original Text:\n{sample_text}\n")

    results = checker.check(sample_text)

    if "error" in results:
        print(f"An error occurred: {results['error']}")
    else:
        print(f"Found {len(results['issues'])} issues.")
        for issue in results['issues']:
            print(
                f"- Category: {issue['rule_category']}, "
                f"Type: {issue['issue_type']}\n"
                f"  Message: {issue['message']}\n"
                f"  Suggestion: {issue['suggestion']}\n"
                f"  Context: {issue['context']}\n"
            )

        print("\n--- Corrected Text (from language-tool) ---")
        print(results['corrected_text'])

    print("\n--- Text Statistics ---")
    stats = checker.get_text_statistics(sample_text)
    if "error" in stats:
        print(stats['error'])
    else:
        for key, value in stats.items():
            print(f"- {key.replace('_', ' ').title()}: {value:.2f}" if isinstance(value, float) else f"- {key.replace('_', ' ').title()}: {value}")

    print("\n--- Paraphrasing Example ---")
    sentence_to_paraphrase = "The group of students is working on their project."
    paraphrases = checker.paraphrase(sentence_to_paraphrase)
    print(f"Original Sentence: '{sentence_to_paraphrase}'")
    print("Suggestions:")
    for p in paraphrases:
        print(f"- {p}")
