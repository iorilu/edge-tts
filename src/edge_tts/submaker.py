"""
SubMaker package for the Edge TTS project.

SubMaker is a package that makes the process of creating subtitles with
information provided by the service easier.
"""

from typing import Any, Dict, Generator, List, Optional, Set, Tuple
import srt


class FilteredText:
    """
    FilteredText allows you to map a text to a filtered version of itself.
    You could use the filtered version and then find the indeces in the
    original text.
    """

    def __init__(self, text: str) -> None:
        self.otext: str = text
        self.ftext: Optional[str] = None
        self.f_to_o_map: Dict[int, int] = {}
        self.o_to_f_map: Dict[int, int] = {}

    def filter_text(self, filter_chars: Set[str]) -> None:
        """
        Filter the text by only keeping the characters in filter_chars.
        """
        self.ftext = ""
        for i, char in enumerate(self.otext):
            if char in filter_chars:
                self.ftext += char
                self.f_to_o_map[len(self.ftext) - 1] = i
                self.o_to_f_map[i] = len(self.ftext) - 1

    def get_original_index(self, filtered_index: int, default: int = -1) -> int:
        """
        Get the original index from the filtered index.
        """
        return self.f_to_o_map.get(filtered_index, default)

    def get_filtered_index(self, original_index: int, default: int = -1) -> int:
        """
        Get the filtered index from the original index.
        """
        return self.o_to_f_map.get(original_index, default)


class SubMaker:
    """
    SubMaker class
    """

    def __init__(self, full_prompt: str) -> None:
        """
        SubMaker constructor.
        """
        self.full_prompt: str = full_prompt
        self.word_boundary_offset: List[Tuple[float, float]] = []
        self.word_boundary_text: List[str] = []
        self.word_boundary_chars: Set[str] = set()

    def add_cue_part(self, timestamp: Tuple[float, float], text: str) -> None:
        """
        Add a subtitle part to the SubMaker object.

        Args:
            timestamp (tuple): The offset and duration of the subtitle.
            text (str): The text of the subtitle.

        Returns:
            None
        """
        self.word_boundary_offset.append((timestamp[0], timestamp[0] + timestamp[1]))
        self.word_boundary_text.append(text)
        self.word_boundary_chars.update(text)

    def make_filtered_text(self) -> FilteredText:
        """
        Get the filtered text from the SubMaker object.

        Returns:
            FilteredText: The filtered text object.
        """
        filtered_text = FilteredText(self.full_prompt)
        for char in (" ", ","):
            self.word_boundary_chars.discard(char)
        filtered_text.filter_text(self.word_boundary_chars)
        return filtered_text

    def get_srt(self, words_in_cue: int = 10) -> str:
        """
        Get the SRT formatted subtitles from the SubMaker object.

        Returns:
            str: The SRT formatted subtitles.
        """

        filtered_text = self.make_filtered_text()
        words_in_cue = max(1, min(words_in_cue, len(self.word_boundary_offset)))

        def get_cue_data() -> Generator[Any, None, None]:
            last_filtered_index = 0

            for i in range(0, len(self.word_boundary_offset), words_in_cue):
                i_end = min(words_in_cue, len(self.word_boundary_offset) - i)

                start_time = self.word_boundary_offset[i][0]
                end_time = self.word_boundary_offset[i + i_end - 1][1]
                text = "".join(self.word_boundary_text[i : i + i_end])
                text = text.replace(" ", "")
                text = text.replace(",", "")

                start_time = srt.timedelta(microseconds=start_time / 10)
                end_time = srt.timedelta(microseconds=end_time / 10)

                fend_index = filtered_text.ftext.find(text, last_filtered_index) + len(text) - 1
                end_index = filtered_text.get_original_index(fend_index, len(self.full_prompt) - 1)
                start_index = filtered_text.get_original_index(last_filtered_index, 0)
                last_filtered_index = fend_index + 1

                yield srt.Subtitle(
                    index=i + 1,
                    start=start_time,
                    end=end_time,
                    content=self.full_prompt[start_index : end_index + 1],
                )

        return srt.compose(get_cue_data())
