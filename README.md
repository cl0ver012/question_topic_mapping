# Security Exam Topic Mapper

## Purpose

This project aims to automate the mapping of security exam questions to their corresponding topics based on a predefined list of topics and keywords. It utilizes a Large Language Model (LLM), specifically OpenAI's GPT-4o-mini, to analyze the questions, answer options, and topic descriptions to determine the most relevant topic for each question. Additionally, the project includes functionality to enhance the topic list by extracting new, specialized keywords from the questions and answers, further improving the accuracy of the mapping process.

The primary goals of this project are:

*   **Accurate Topic Mapping:** To accurately map security exam questions to their respective topics.
*   **Keyword Enhancement:** To improve the topic list by extracting relevant keywords from the question data.
*   **Automation:** To automate the process of topic mapping and keyword extraction, saving time and effort.
*   **Data-Driven Insights:** To provide a structured dataset of questions mapped to topics, enabling better analysis and understanding of the exam content.

## Project Structure

The project consists of the following main components:

*   **`map_topics.py`:** The primary script that performs the topic mapping. It loads the questions and topics, interacts with the LLM to map questions to topics, and saves the results.
*   **`extract_keywords.py`:** A script that extracts new keywords for each topic based on the questions mapped to that topic. It uses the LLM to analyze the questions and generate relevant keywords.
*   **`data/Questions to be Mapped.csv`:** A CSV file containing the security exam questions, answer options, and (after running `map_topics.py`) the mapped topic number and name.
*   **`data/Topics Test Data.csv`:** A CSV file containing the list of predefined topics, their descriptions, and associated keywords.
*   **`data/Updated Topics Test Data.csv`:** A CSV file generated after running `extract_keywords.py`, containing the updated list of topics with enhanced keywords.
*   **`requirements.txt`:** A file listing the Python dependencies required for the project.

## How to Run

### Prerequisites

1. **Python 3.8 or higher:** Ensure you have Python 3.8 or a later version installed on your system.
2. **OpenAI API Key:** You need an OpenAI API key to use the GPT-4o-mini model. Obtain one from the OpenAI website.

### Installation

1. **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```
2. **Create and activate a virtual environment (recommended):**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Linux/macOS
    .venv\Scripts\activate  # On Windows
    ```
3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4. **Set your OpenAI API key:**
    *   Create a `.env` file in the project's root directory.
    *   Add the following line to the `.env` file, replacing `YOUR_API_KEY` with your actual API key:
        ```
        OPENAI_API_KEY=YOUR_API_KEY
        ```

### Running the Scripts

1. **Topic Mapping (`map_topics.py`):**
    *   This script maps the questions in `data/Questions to be Mapped.csv` to the topics in `data/Topics Test Data.csv`.
    *   Run the script from the project's root directory:
        ```bash
        python map_topics.py
        ```
    *   The script will output the mapped questions, topic numbers, confidence scores, and any notes to the console.
    *   The results will be saved in `Updated Questions to be Mapped.csv`, with new columns for "Topic Number" and "Topic Name".

2. **Keyword Extraction (`extract_keywords.py`):**
    *   This script extracts new keywords for each topic based on the questions mapped to it.
    *   Run the script from the project's root directory:
        ```bash
        python extract_keywords.py
        ```
    *   The script will output the new keywords for each topic to the console.
    *   The updated topics with new keywords will be saved in `data/Updated Topics Test Data.csv`.

## Important Notes

*   The accuracy of the topic mapping and keyword extraction depends on the quality of the LLM and the clarity of the topic descriptions and questions.
*   The `extract_keywords.py` script can take a significant amount of time to run, depending on the number of questions and topics.
*   It's recommended to review the output of both scripts to ensure the accuracy of the results and make any necessary adjustments to the topic descriptions or keywords.
