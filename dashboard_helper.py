#!/usr/bin/env python3

import io
import json
import os
import time

import pandas as pd
import requests
import streamlit as st
from rich.console import Console

console = Console()


def get_prompt(csv_content):
    prompt = f"""
    You are a timesheet data analyst.

    **Input:** Raw CSV content representing work entries.
    CSV:
    {csv_content}

    **Task:**
    1.  **Columns:** List all unique column headers.
    2.  **Time_Column:** Among all column headers, identify the column that represent time spent on the task.
    3.  **Date_Column:** Among all column headers, identify the column that represent the date.
    4.  **Summary:** Analyze the timesheet data to identify the major, distinct work activities. For each major activity, summarize its overall time commitment. Find its subactivities. Each subactivity of an activity must be summarized as points.

    **Output as JSON 1st key being Columns, 2nd key being Time_Column, 3rd key being Activities_Summary":**
      1. "Columns": ["Column Name 1", "Column Name 2"] obtained in Task 1
      2. "Time_Column": Column obtained in Task 2
      3. "Date_Column": Column obtained in Task 3
      4. "Activities_Summary": Summary (as a string) obtained in Task 4 as given below.
          1. Activity1 (bold letters): Time Spent - first major point
              - subtask1 in concise form as a point below the Activity1
              - subtask2 in concise form as a point below the subtask1
          2. Activity2 (bold letters): Time Spent - second major point
              - subtask1 in concise form as a point below the Activity2
              - subtask2 in concise form as a point below the subtask1
    """
    return prompt


@st.cache_data(show_spinner="Summarizing activities...")
def summarize_timesheet_with_gemini(df: pd.DataFrame) -> str:
    """
    Takes a pandas DataFrame containing timesheet data, converts it to a CSV string,
    sends it to the Gemini API for summarization, and returns the summarized
    activities as a string.

    Args:
        df (pd.DataFrame): The pandas DataFrame containing the timesheet data.

    Returns:
        str: A bulleted list of major activities summarized by Gemini,
             or an error message if the API call fails.
    """
    # Convert the DataFrame to CSV content string
    # index=False prevents writing the DataFrame index as a column in the CSV string
    csv_content = df.to_csv(index=False)

    # Gemini API configuration
    api_key = os.getenv("GEMINI_API_KEY")
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    # Craft the prompt for Gemini
    prompt = get_prompt(csv_content)

    # Prepare the payload for the API request
    payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}
    max_retries = 3  # Maximum number of retries
    retry_delay_seconds = 5  # Delay between retries in seconds

    # Send request to Gemini
    print("Sending request to Gemini API...")
    for attempt in range(max_retries):
        console.print(f"Attempt#: {attempt}", style="bold red")
        try:
            response = requests.post(api_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
            result = response.json()

            # Extract the generated text from the response
            if result and result.get("candidates") and len(result["candidates"]) > 0:
                generated_text = (
                    result["candidates"][0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "No summary found.")
                )
                console.print(
                    f"Text Generated in attempt#: {attempt}", style="bold green"
                )
                # console.print(f"Text Generated: {generated_text}", style="bold blue")
                return generated_text
            else:
                return f"Error: Unexpected API response structure: {json.dumps(result, indent=2)}"

        except requests.exceptions.HTTPError as http_err:
            # Check for 503 Service Unavailable or other server errors (5xx)
            if http_err.response.status_code >= 500 and attempt < max_retries - 1:
                print(
                    f"Attempt {attempt + 1}/{max_retries}: Server error ({http_err.response.status_code}). Retrying in {retry_delay_seconds} seconds..."
                )
                time.sleep(retry_delay_seconds)
            else:
                # Re-raise the error if it's not a server error or if max retries reached
                return f"Error connecting to Gemini API after {attempt + 1} attempts: {http_err}"
        except requests.exceptions.ConnectionError as conn_err:
            # Handle network-related errors (e.g., DNS failure, refused connection)
            if attempt < max_retries - 1:
                print(
                    f"Attempt {attempt + 1}/{max_retries}: Connection error. Retrying in {retry_delay_seconds} seconds..."
                )
                time.sleep(retry_delay_seconds)
            else:
                return f"Error connecting to Gemini API after {attempt + 1} attempts: {conn_err}"
        except requests.exceptions.Timeout as timeout_err:
            # Handle request timeouts
            if attempt < max_retries - 1:
                print(
                    f"Attempt {attempt + 1}/{max_retries}: Timeout error. Retrying in {retry_delay_seconds} seconds..."
                )
                time.sleep(retry_delay_seconds)
            else:
                return f"Error connecting to Gemini API after {attempt + 1} attempts: {timeout_err}"
        except json.JSONDecodeError:
            return f"Error decoding JSON response: {response.text}"
        except Exception as e:
            # Catch any other unexpected errors
            return f"An unexpected error occurred during API call: {e}"
    return "Failed to get a summary after multiple retries."  # Should ideally not be reached if max_retries is handled correctly
