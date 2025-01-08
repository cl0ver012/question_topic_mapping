import pandas as pd
from pydantic import BaseModel, Field, field_validator
import pydantic
from typing import Optional, List
from openai import AsyncOpenAI  # Import AsyncOpenAI
import json
import os
from enum import Enum
import asyncio  # Import asyncio
from typing import Dict

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------
# 1. Define the Enumerated Datatype (Topic Options)
# ---------------------------------------------------------------------

# Load the topics from the CSV
topics_df = pd.read_csv("data/Topics Test Data.csv")

# Create an Enum class dynamically, inheriting from str and Enum
class TopicEnum(str, Enum):
    pass

# Dynamically add members to the TopicEnum using add_topic_member method
def add_topic_member(cls, name: str, value: str):
    # Correctly create a new enum member dynamically for a string-based Enum
    new_member = str.__new__(cls, value)  # Use str.__new__ here
    new_member._name_ = name
    new_member._value_ = value

    # Add the member to the enum class
    cls._member_map_[name] = new_member
    cls._value2member_map_[value] = new_member

    return new_member

for index, row in topics_df.iterrows():
    topic_number_str = str(row['Topic Number'])
    member_name = f"TOPIC_{topic_number_str.replace('.', '_').replace('-', '_')}"
    add_topic_member(TopicEnum, member_name, topic_number_str)  # Use string value

# ---------------------------------------------------------------------
# 2. Define the Structured Output Schema (Using Pydantic)
# ---------------------------------------------------------------------

class QuestionMapping(BaseModel):
    topic_number: TopicEnum = Field(..., description="The topic number to which the question is mapped.")
    confidence: Optional[float] = Field(..., description="Confidence score of the mapping (0.0 to 1.0).")
    notes: Optional[str] = Field(..., description="Any notes or explanations regarding the mapping, especially if unsure.")
    new_keywords: Optional[List[str]] = Field(..., description="New keywords extracted from the question that can enhance the topic.")

# ---------------------------------------------------------------------
# 3. Process Questions and Generate Output (Asynchronous)
# ---------------------------------------------------------------------

async def process_question(row: pd.Series, topic_list_str: str) -> Dict:
    """Asynchronously processes a single question, including answer options."""
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    question_text = row['Question']
    
    # Include answer options in the prompt
    answer_options = f"""
    A. {row['Answer A']}
    B. {row['Answer B']}
    C. {row['Answer C']}
    D. {row['Answer D']}
    E. {row['Answer E']}
    F. {row['Answer F']}
    G. {row['Answer G']}
    H. {row['Answer H']}
    Correct Answer(s). {row['Correct Answer(s)']}
    """

    prompt = f"""
    Instructions:
    You are an AI that maps questions to the most relevant topic from a predefined list.
    Analyze the question below, along with the provided answer options, and determine the best matching topic number.
    Provide a confidence score between 0.0 and 1.0 indicating how sure you are of the mapping.
    If you are unsure, provide notes explaining your reasoning or difficulties.
    Return the result in a JSON format that validates against the provided schema.

    Topics:
    {topic_list_str}

    Question:
    {question_text}
    
    Answer Options:
    {answer_options}
    """

    try:
        response = await client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format=QuestionMapping
        )

        response_json = json.loads(response.choices[0].message.content)
        mapped_question = QuestionMapping.model_validate(response_json)
        print("========")
        print({
            "Question": question_text,
            "Topic Number": mapped_question.topic_number.value,
            "Confidence": mapped_question.confidence,
            "Notes": mapped_question.notes,
            "New Keywords": mapped_question.new_keywords
        })
        return {
            "Question": question_text,
            "Topic Number": mapped_question.topic_number.value,
            "Confidence": mapped_question.confidence,
            "Notes": mapped_question.notes,
            "New Keywords": mapped_question.new_keywords
        }
    except (json.JSONDecodeError, pydantic.ValidationError) as e:
        print(f"Error processing response for question '{question_text}': {e}")
        return {
            "Question": question_text,
            "Topic Number": None,
            "Confidence": None,
            "Notes": f"Error processing response: {e}",
            "New Keywords": None
        }
    finally:
        await client.close()

async def main():
    # Load questions from CSV
    questions_df = pd.read_csv("data/Questions to be Mapped.csv")

    # Prepare the topic list for the prompt
    topic_list_str = ""
    for index, row in topics_df.iterrows():
        topic_list_str += f"- Topic {row['Topic Number']}: {row['Topic Name']} (Keywords: {row['Topic Keywords']})\n"

    # Create a list of tasks for each question
    tasks = [process_question(row, topic_list_str) for index, row in questions_df.iterrows()]

    # Execute tasks concurrently
    mapped_questions = await asyncio.gather(*tasks)

    # Convert results to DataFrame
    mapped_questions_df = pd.DataFrame(mapped_questions)

    # Add Topic Name to the DataFrame
    mapped_questions_df['Topic Name'] = mapped_questions_df['Topic Number'].apply(
        lambda x: topics_df[topics_df['Topic Number'] == x]['Topic Name'].iloc[0] if x in topics_df['Topic Number'].values else None
    )

    # Merge mapped topics back into the original questions DataFrame
    questions_df['Topic Number'] = mapped_questions_df['Topic Number']
    questions_df['Topic Name'] = mapped_questions_df['Topic Name']

    # Save the updated DataFrame to CSV file
    questions_df.to_csv("data/Updated Questions to be Mapped.csv", index=False)

    print("Processing complete. Check 'Questions to be Mapped.csv'")

if __name__ == "__main__":
    asyncio.run(main())