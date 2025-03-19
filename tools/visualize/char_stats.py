import streamlit as st

from tools.extract.config import CHUNK_SIZE
from tools.extract.stream_reader import StreamReader

from tools.transform.char_stats import CharStatistics

from tools.visualize.localization.manager import LocalizationManager
import tools.visualize.localization.english.india as locale_fall_back

LOCALE = LocalizationManager(locale_fall_back)

def main():
    st.title(LOCALE.char_statistics_dashboard_title)

    preferred_locale = st.selectbox(LOCALE.enter_preferred_localization_label, LOCALE.available.keys())
    LOCALE.load_locale(preferred_locale)

    folder_path = st.text_input(LOCALE.enter_folder_path_label, value="content/")
    chunk_size = st.number_input(LOCALE.enter_chunk_size_label, value=CHUNK_SIZE, min_value=1, step=1)

    st.write(LOCALE.processing_folder_label % folder_path)

    reader = StreamReader(chunk_size=chunk_size)
    stats_collector = CharStatistics(reader)
    folder_stats = stats_collector.collect(folder_path)

    # ===
    st.subheader(LOCALE.char_statistics_overall_data_table_title)
    folder_data = [
        {
            LOCALE.field_total_chars_count: folder_stats.total_chars,
            LOCALE.field_unique_chars_count: len(folder_stats.unique_char_set),
        }
    ]
    st.table(folder_data)

    # ===
    st.subheader(LOCALE.char_statistics_file_data_table_title)
    file_data = [
        {
            LOCALE.field_file_path: file_path,
            LOCALE.field_total_chars_count: file_stats.total_chars,
            LOCALE.field_unique_chars_count: len(file_stats.unique_char_set),
        } for file_path, file_stats in folder_stats.file_stats.items()
    ]
    file_data_sort_options = [
        LOCALE.field_file_path,
        LOCALE.field_total_chars_count,
        LOCALE.field_unique_chars_count,
    ]
    file_data_sort_by = st.selectbox(LOCALE.enter_preferred_sort_label, file_data_sort_options)
    sorted_file_data = sorted(
        file_data,
        key=lambda x: x[file_data_sort_by],
    )
    st.table(sorted_file_data)

    # ===
    with st.expander(LOCALE.char_statistics_char_data_table_title):
        st.subheader(LOCALE.char_statistics_char_data_table_title)
        char_data = [
            {
                LOCALE.field_char_codepoint: char,
                LOCALE.field_char: f"`{chr(char)}`",
                LOCALE.field_frequency: frequency,
            } for char, frequency in folder_stats.unique_char_set.items()
        ]
        char_data_sort_options = [
            LOCALE.field_char_codepoint,
            LOCALE.field_char,
            LOCALE.field_frequency,
        ]
        char_data_sort_by = st.selectbox(LOCALE.enter_preferred_sort_label, char_data_sort_options)
        sorted_char_data = sorted(
            char_data,
            key=lambda x: x[char_data_sort_by],
        )
        st.table(sorted_char_data)

    # ===
    with st.expander(LOCALE.char_statistics_char_file_data_table_title):
        st.subheader(LOCALE.char_statistics_char_file_data_table_title)
        char_file_preferred_file_path = st.selectbox(LOCALE.select_file_label, folder_stats.file_stats.keys())
        char_file_data = [
            {
                LOCALE.field_char_codepoint: char,
                LOCALE.field_char: f"`{chr(char)}`",
                LOCALE.field_frequency: frequency,
            } for char, frequency in folder_stats.file_stats[char_file_preferred_file_path].unique_char_set.items()
        ]
        char_file_data_sort_by = st.selectbox(LOCALE.enter_preferred_sort_label, char_data_sort_options, key='char-file-data-sort-by')
        sorted_char_file_data = sorted(
            char_file_data,
            key=lambda x: x[char_file_data_sort_by],
        )
        st.table(sorted_char_file_data)

if __name__ == "__main__":
    main()
