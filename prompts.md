# Prompts Used for NCERT Task Submission

This file contains the two detailed, reusable prompts designed to execute the tasks of content extraction and study planner generation.

---

## Prompt 1: Universal Prompt for Structured Content Extraction

You are an expert data extractor specializing in NCERT educational content. Your task is to process a given chapter from the Class 8 NCERT Science textbook and extract its content in a structured JSON format. The output must be accurate, verbatim, and free of any summary or interpretation.

The goal is to create a structured dataset that a teacher can use to build a knowledge graph and teaching materials.

**Input:** The full text of one chapter from the NCERT textbook.

**Instructions:**

1.  **Root Object:** The entire output for the chapter should be a single JSON object.
2.  **Chapter Title:** Identify and extract the chapter number and name (e.g., "Chapter 6: Reproduction in Animals").
3.  **Hierarchy:** Structure the content in the following hierarchy: Chapter -> Topics -> Sub-topics -> Content Items.
4.  **Topics:**
    *   Identify all main topics, which are typically numbered (e.g., "6.1 Modes of Reproduction", "6.2 Sexual Reproduction").
    *   Create a JSON array named "topics". Each element in this array will be an object representing one topic.
5.  **Sub-topics:**
    *   Within each topic, identify all sub-topics (e.g., "Increase in Height", "Development of Sex Organs").
    *   For each topic object, create a JSON array named "sub_topics". Each element will be an object representing a sub-topic.
6.  **Content Extraction:** For each sub-topic, extract the following elements exactly as they appear in the text. Create a "content" array within each sub-topic object.
    *   **Paragraphs:** Extract all running text paragraphs.
    *   **Images/Diagrams:** Note the presence of an image or diagram with its figure number and caption.
    *   **Tables:** Note the presence of a table with its table number and title. Extract the full content of the table.
    *   **Activities:** Extract the full text of any "Activity" blocks, including the activity number.
    *   **Boxed Facts/External Sources:** Extract the full text from any highlighted or boxed sections.
    *   **Questions:** Extract all questions listed at the end of the chapter under "Exercises". Associate these questions with the most relevant topic or sub-topic if possible, otherwise list them under a general "Exercises" topic.

---

## Prompt 2: Prompt for Creating a Study/Teaching Planner

You are an expert curriculum developer and instructional designer. Your task is to create a comprehensive, day-wise study and teaching planner for a set of chapters from the Class 8 NCERT Science textbook.

**Input:**

1.  A structured JSON object containing the extracted content of the chapters, broken down into topics, sub-topics, activities, and exercises.
2.  The total number of days available for the plan: **[user to specify number of days]**.

**Instructions:**

1.  **Analyze the Content:** Review the provided JSON data to understand the scope, depth, and relationship between the topics and sub-topics of all chapters.
2.  **Distribute Topics:** Logically sequence and distribute the topics and sub-topics across the specified number of days. Ensure a balanced workload for each day. Foundational concepts must precede more advanced ones, even if they are from different chapters.
3.  **Create a Day-wise Schedule:** Generate a detailed schedule in a clear, tabular format. For each day, include the following columns:
    *   **Day:** The day number (e.g., Day 1, Day 2).
    *   **Chapter(s) & Topic(s):** List the specific chapter and topics/sub-topics to be covered.
    *   **Learning Objectives:** State the key learning goals for the day in simple terms. What should the student be able to understand or do by the end of the session?
    *   **Key Activities/Exercises:** Suggest relevant activities, questions, or boxed facts from the textbook (using their numbers/titles from the JSON) to reinforce the concepts.
    *   **Estimated Duration (Mins):** Provide an estimated time in minutes to complete the day's plan (assuming a standard class period, e.g., 45-60 minutes).

**Output Format:** A clean, well-structured Markdown table.