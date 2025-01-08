import pandas as pd
from pydantic import BaseModel, Field
from typing import List
from openai import AsyncOpenAI
import json
import os
import asyncio
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class Keywords(BaseModel):
    keywords: List[str] = Field(
        ...,
        description="List of the new keywords of the topic"
    )

async def extract_keywords_for_topic(
    topic_number: str,
    topic_name: str,
    current_keywords: str,
    questions_context: str,
    example_topics_str: str,
) -> List[str]:
    """
    Extracts new keywords for a given topic using the LLM.
    """
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = f"""
    Instructions:
    You are an AI that extracts relevant and specific keywords for a given topic based on a set of questions and answers.
    The keywords should be general concepts or specialized phrases related to the topic, NOT specific to the questions.
    Avoid extracting keywords that are already present in the current keyword list.
    Provide a list of new keywords that can enhance the topic's description.
    These keywords should be new keywords that are not included in the current keyword list.
    Only extract the most relevant keywords.
    You don't have to extract many, but you must extract high quality keywords.
    It is ok just extract 2-3 keywords.
    If you can not find any relevant keywords, just return empty list.
    These topics and questions are comes from the security exam.
    So you need to pick up keywords that is comes from the security related area

    Topic Number: {topic_number}
    Topic Name: {topic_name}
    Current Keywords: {current_keywords}

    Examples of Topics and Keywords:
    {example_topics_str}

    Questions and Answers Context:
    {questions_context}

    Return the result as a JSON array of strings.
    """

    try:
        response = await client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format=Keywords
        )

        response_json = json.loads(response.choices[0].message.content)
        new_keywords = Keywords.model_validate(response_json).keywords
        # new_keywords = response_json.get("keywords", [])
        print(f"New keywords for topic {topic_number}: {new_keywords}")
        return new_keywords
    except Exception as e:
        print(f"Error extracting keywords for topic {topic_number}: {e}")
        return []
    finally:
        await client.close()

async def main():
    """
    Main function to extract keywords for all topics.
    """
    # Load data
    questions_df = pd.read_csv("data/Updated Questions to be Mapped.csv")
    topics_df = pd.read_csv("data/Topics Test Data.csv")

    # Add new column for new keywords
    topics_df['New Topic Keywords'] = ''

    # Group questions by topic
    grouped_questions = questions_df.groupby("Topic Number")

    # Prepare examples of topics and keywords
    example_topics_str = ""
    for index, row in topics_df[topics_df['Topic Keywords'].notna()].sample(n=20).iterrows():
        keywords = [k.strip() for k in row['Topic Keywords'].split('-')]
        example_topics_str += f"- Topic: {row['Topic Name']}, Keywords: {keywords}\n"

    # Create tasks for each topic
    tasks = []
    for topic_number, group in grouped_questions:
        topic_row = topics_df[topics_df["Topic Number"] == topic_number].iloc[0]
        topic_name = topic_row["Topic Name"]
        current_keywords = topic_row["Topic Keywords"]

        # Create context string from questions and answers
        questions_context = ""
        for index, row in group.iterrows():
            questions_context += f"Question: {row['Question']}\n"
            questions_context += f"A. {row['Answer A']}\n"
            questions_context += f"B. {row['Answer B']}\n"
            questions_context += f"C. {row['Answer C']}\n"
            questions_context += f"D. {row['Answer D']}\n"
            questions_context += f"E. {row['Answer E']}\n"
            questions_context += f"F. {row['Answer F']}\n"
            questions_context += f"G. {row['Answer G']}\n"
            questions_context += f"H. {row['Answer H']}\n"
            questions_context += f"Correct Answer(s): {row['Correct Answer(s)']}\n\n"

        tasks.append(
            extract_keywords_for_topic(
                topic_number, topic_name, current_keywords, questions_context, example_topics_str
            )
        )

    # Execute tasks concurrently
    new_keywords_results = await asyncio.gather(*tasks)

    # Update New Topic Keywords column with results
    for topic_number, new_keywords in zip(grouped_questions.groups.keys(), new_keywords_results):
        if new_keywords:  # Only update if there are new keywords
            mask = topics_df["Topic Number"] == topic_number
            topics_df.loc[mask, "New Topic Keywords"] = ", ".join(new_keywords)

    # Save updated topics_df
    topics_df.to_csv("data/Updated Topics Test Data.csv", index=False)
    print("Keyword extraction complete. Check 'Updated Topics Test Data.csv'")

if __name__ == "__main__":
    asyncio.run(main())