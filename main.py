#!/usr/bin/env python3

import json

import pandas as pd
import streamlit as st
from rich.console import Console

from dashboard_helper import summarize_timesheet_with_gemini

console = Console()


def summarize(df):
    """
    Takes a pandas dataframe, pass the dataframe to the Gemini API and get the response.

    Args:
        df : Pandas dataframe.

    Returns:
        str: Relevant columns in the table, column representing time spent and
        the
    """
    try:
        # Call the summarization function with the DataFrame
        r = summarize_timesheet_with_gemini(df)
        if ("error" in r.lower()) or ("fail" in r.lower()):
            return "error"
    except Exception as e:
        console.print("Gemini API call error")
        st.error(f"An unexpected error occurred during the Gemini API call: {e}")
        return "error"

    return r


def extract_data_from_gemini_response(response_data):
    """
    Takes response data from Gemini API call and extract the required details.

    Args:
        response_data : Response data from Gemini API call.

    Returns:
        columns, time_column, date_column, summary: Relevant columns in the
        table, column representing time spent, column representing date and
        the summary of the table data
    """
    columns = []
    time_column = ""
    date_column = ""
    summary = ""
    try:
        # console.print(type(response_data))
        # console.print(response_data)
        # print("*"*100)
        result = json.loads(
            response_data[response_data.find("{") : response_data.rfind("}") + 1].strip()
        )
        columns = result["Columns"]
        console.print(f"Columns identified: {columns}", style="bold blue")
        time_column = result["Time_Column"]
        console.print(f"Time Column identified: {time_column}", style="bold blue")
        date_column = result["Date_Column"]
        console.print(f"Date Colum identifies: {date_column}", style="bold blue")
        summary = result["Activities_Summary"]
        # console.print(summary)
        # print("*"*100)
        return columns, time_column, date_column, summary
    except Exception as e:
        console.print(f"Extraction failed due to :{e}")
        return columns, time_column, date_column, summary


def main():
    """
    A streamlit application to analyze the timesheet details.

    """
    # Title
    st.title("Timesheet Analysis")
    # Use a placeholder or initial message
    st.info("Please upload your timesheet CSV file to begin.")
    console.print("Title Displayed", style="bold green")

    # Initialize session state variables if they don't exist
    if "df" not in st.session_state:
        st.session_state.df = None
    if "gemini_result" not in st.session_state:
        st.session_state.gemini_result = None
    if "columns_from_gemini" not in st.session_state:
        st.session_state.columns_from_gemini = []
    if "time_column" not in st.session_state:
        st.session_state.time_column = ""
    if "date_column" not in st.session_state:
        st.session_state.date_column = ""
    if "summary_text" not in st.session_state:
        st.session_state.summary_text = ""
    if "show_analysis" not in st.session_state:
        st.session_state.show_analysis = False  # Flag to control rendering of analysis sections
    console.print("Session Initiated", style="bold green")

    # Upload File
    uploaded_file = st.file_uploader("Upload your timesheet", type="csv")
    if uploaded_file is not None:
        # console.print(f"Uploaded File: {uploaded_file.name}", style="bold green")
        # try:
        # df = pd.read_csv(uploaded_file)
        try:
            df = pd.read_csv(uploaded_file)
            # Store in session state. This will trigger a rerun if df changes.
            st.session_state.df = df
            st.success("File uploaded and read successfully!")
            st.session_state.gemini_result = None
        except Exception as e:
            st.error(f"Error reading CSV file: {e}. Please ensure it's a valid CSV.")
            st.session_state.df = None  # Clear df if reading failed
            st.session_state.gemini_result = None  # Clear result too
            st.session_state.df = None
            st.session_state.last_uploaded_file_name = None
            st.session_state.columns_from_gemini = []
            st.session_state.time_column = ""
            st.session_state.date_column = ""
            st.session_state.summary_text = ""
            st.session_state.show_analysis = False

        # Summarize tasks
        # Use a button to trigger the summarization
        if st.button("Summarize Activities"):
            # Clear previous summary before generating a new one
            st.session_state.gemini_result = None
            st.session_state.show_analysis = False

            # Call the summarization function with the DataFrame
            response_data = summarize(df)
            # If the gemini api call returns any error exit
            if response_data == "error":
                console.print("Gemini API call error")
            else:
                st.session_state.gemini_result = response_data
                # st.success("AI Summary generated successfully!")

            # Display summary and filtering options only if gemini_result is available
            if st.session_state.gemini_result:
                # Extract column names of the data and summary of the activities from gemini response
                (
                    columns,
                    time_column,
                    date_column,
                    summary,
                ) = extract_data_from_gemini_response(response_data)
                st.session_state.columns_from_gemini = columns
                st.session_state.time_column = time_column
                st.session_state.date_column = date_column
                st.session_state.summary_text = summary
                st.session_state.show_analysis = True  # Now we can show analysis sections

        if st.session_state.columns_from_gemini:  # If columns are identified from the file
            # Identify if the file can be processed based on the column names returned from Gemini and the current header row
            columns_df = df.columns.tolist()
            columns = st.session_state.columns_from_gemini
            # If header rows don't match, file cannot be processed
            if (len(set(columns) & set(columns_df))) < (len(columns) / 2):
                st.warning(
                    "CSV should have only a single header. Reupload the file after deleting any titles from the header"
                )
                st.session_state.df = None  # Clear df if reading failed
                st.session_state.gemini_result = None  # Clear result too
                st.session_state.last_uploaded_file_name = None
                st.session_state.columns_from_gemini = []
                st.session_state.summary_text = ""
                st.session_state.show_analysis = False
            else:
                if st.session_state.summary_text:  # If summary obtained
                    summary = st.session_state.summary_text  # Get summary
                    st.subheader("Major Activities Summary:")
                    st.markdown(summary)  # Display summary
                    st.success("AI Summary generated successfully!")

                # Filter Data based on columns
                st.subheader("Filter Data")
                selected_column = st.selectbox("Choose a column to filter by", columns)
                unique_values = df[selected_column].unique()
                selected_value = st.selectbox("select_value", unique_values)
                filtered_df = df[df[selected_column] == selected_value]
                st.write(filtered_df)
                console.print(f"{selected_value} filter applied successfully", style="bold green")

                # Calculate time taken for the selected activities
                if st.session_state.time_column != "":
                    time_column = st.session_state.time_column
                    time = filtered_df[time_column].sum()
                    total_time = df[time_column].sum()
                    percentage = round((time / total_time) * 100)
                    percentage_string = str(percentage) + "%"
                    date_column = st.session_state.date_column
                    st.metric(label="Time spent(In hours)", value=time)
                    st.metric(label="Time spent(In percentage)", value=percentage_string)

                    # Plot the time taken for the selected activities
                    st.subheader("Plot Data")
                    x_column = date_column
                    y_column = time_column
                    if st.button("Generate Plot"):
                        st.bar_chart(filtered_df.set_index(x_column)[y_column])
                    console.print("Generated plot", style="bold green")
                    print("*" * 100)

        data_available = True
        try:
            if st.session_state.df is None:
                data_available = False
        except Exception:
            data_available = True

        if (st.session_state.summary_text == "") and data_available:
            st.info("Click 'Summarize Activities' to get an AI-generated summary.")
    else:
        console.print("Waiting for file upload...", style="bold yellow")
        st.warning("No file uploaded yet.")


if __name__ == "__main__":
    main()
