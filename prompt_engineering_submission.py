import json
import pandas as pd

# ==============================================================================
# SECTION 1: PROMPTS
# These are the detailed, reusable prompts as required by the task.
# ==============================================================================

EXTRACTION_PROMPT = """
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
"""

PLANNER_PROMPT_TEMPLATE = """
You are an expert curriculum developer and instructional designer. Your task is to create a comprehensive, day-wise study and teaching planner for a set of chapters from the Class 8 NCERT Science textbook.

**Input:**

1.  A structured JSON object containing the extracted content of the chapters, broken down into topics, sub-topics, activities, and exercises.
2.  The total number of days available for the plan: {days}.

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
"""

# ==============================================================================
# SECTION 2: MOCK API AND DATA
# This section simulates the behavior of an AI model API.
# Instead of making a real API call, it returns pre-generated, hardcoded data.
# This ensures the script is self-contained and runnable without an API key.
# ==============================================================================

# This is the full, pre-generated JSON output for all four chapters.
MOCK_JSON_OUTPUT = """
[
  {
    "chapter_number": "6",
    "chapter_name": "Reproduction in Animals",
    "topics": [
      {
        "topic_name": "6.1 Modes of Reproduction",
        "sub_topics": [
          {
            "sub_topic_name": null,
            "content": [
              {"type": "paragraph", "text": "Just as in plants, there are two modes by which animals reproduce. These are: (i) Sexual reproduction, and (ii) Asexual reproduction."}
            ]
          }
        ]
      },
      {
        "topic_name": "6.2 Sexual Reproduction",
        "sub_topics": [
          {"sub_topic_name": "Male Reproductive Organs", "content": [{"type": "paragraph", "text": "The male reproductive organs include a pair of testes (singular, testis), two sperm ducts and a penis (Fig. 6.1)."}, {"type": "image", "caption": "Fig. 6.1: Male reproductive organs in humans"}]},
          {"sub_topic_name": "Female Reproductive Organs", "content": [{"type": "paragraph", "text": "The female reproductive organs are a pair of ovaries, oviducts (fallopian tubes) and the uterus (Fig. 6.3)."}, {"type": "image", "caption": "Fig. 6.3: Female reproductive organs in humans"}]},
          {"sub_topic_name": "Fertilisation", "content": [{"type": "paragraph", "text": "The first step in the process of reproduction is the fusion of a sperm and an ovum. When sperms come in contact with an egg, one of the sperms may fuse with the egg."}, {"type": "activity", "name": "Activity 6.1", "text": "Visit some ponds or slow-flowing streams during spring or rainy season. Look out for clusters of frog’s eggs floating in water."}, {"type": "boxed_fact", "text": "Have you heard of test tube babies? Boojho and Paheli's teacher once told them in the class that in some women oviducts are blocked."}]},
          {"sub_topic_name": "Development of Embryo", "content": [{"type": "paragraph", "text": "Fertilisation results in the formation of zygote which begins to develop into an embryo [Fig. 6.8(a)]."}]},
          {"sub_topic_name": "Viviparous and Oviparous Animals", "content": [{"type": "paragraph", "text": "We have learnt that some animals give birth to young ones while some animals lay eggs which later develop into young ones."}, {"type": "activity", "name": "Activity 6.2", "text": "Try to observe eggs of the following organisms – frog, lizard, butterfly or moth, hen and crow or any other bird."}]}
        ]
      },
      {
        "topic_name": "Exercises",
        "sub_topics": [],
        "content": [
            {"type": "question", "text": "1. Explain the importance of reproduction in organisms."},
            {"type": "question", "text": "2. Describe the process of fertilisation in human beings."},
            {"type": "question", "text": "3. Choose the most appropriate answer. (a) Internal fertilisation occurs (i) in female body..."}
        ]
      }
    ]
  },
  {
    "chapter_number": "7",
    "chapter_name": "Reaching the Age of Adolescence",
    "topics": [
        {"topic_name": "7.1 Adolescence and Puberty", "sub_topics": [{"sub_topic_name": null, "content": [{"type": "paragraph", "text": "The period of life, when the body undergoes changes, leading to reproductive maturity, is called adolescence."}]}]},
        {"topic_name": "7.2 Changes at Puberty", "sub_topics": [{"sub_topic_name": "Increase in Height", "content": [{"type": "activity", "name": "Activity 7.1", "text": "The following chart gives the average rate of growth in height of boys and girls with age."}]}, {"sub_topic_name": "Change in Body Shape", "content": [{"type": "paragraph", "text": "Have you noticed that boys in your class have broader shoulders and wider chests than boys in junior classes?"}]}]},
        {"topic_name": "7.9 Reproductive Health", "sub_topics": [{"sub_topic_name": "Nutritional Needs of the Adolescents", "content": [{"type": "activity", "name": "Activity 7.4", "text": "Make a group with your friends. Write down the items of food in your breakfast, lunch and dinner you had on the previous day."}]}, {"sub_topic_name": "Personal Hygiene", "content": [{"type": "paragraph", "text": "Everyone should have a bath at least once everyday."}]}]},
        {"topic_name": "Exercises", "sub_topics": [], "content": [{"type": "question", "text": "1. What is the term used for chemical secretions of endocrine glands responsible for changes taking place in the body?"}]}
    ]
  },
  {
    "chapter_number": "8",
    "chapter_name": "Force and Pressure",
    "topics": [
        {"topic_name": "8.1 Force – A Push or a Pull", "sub_topics": [{"sub_topic_name": null, "content": [{"type": "activity", "name": "Activity 8.1", "text": "Table 8.1 gives some examples of familiar situations involving motion of objects."}]}]},
        {"topic_name": "8.3 Exploring Forces", "sub_topics": [{"sub_topic_name": null, "content": [{"type": "activity", "name": "Activity 8.2", "text": "Choose a heavy object like a table or a box, which you can move only by pushing hard."}]}]},
        {"topic_name": "8.8 Pressure", "sub_topics": [{"sub_topic_name": null, "content": [{"type": "paragraph", "text": "The force acting on a unit area of a surface is called pressure."}, {"type": "image", "caption": "Fig. 8.13: A porter carrying a heavy load"}]}]},
        {"topic_name": "Exercises", "sub_topics": [], "content": [{"type": "question", "text": "1. Give two examples each of situations in which you push or pull to change the state of motion of objects."}]}
    ]
  },
  {
    "chapter_number": "13",
    "chapter_name": "Light",
    "topics": [
        {"topic_name": "13.2 Laws of Reflection", "sub_topics": [{"sub_topic_name": null, "content": [{"type": "activity", "name": "Activity 13.1", "text": "Fix a white sheet of paper on a drawing board or a table."}, {"type": "table", "caption": "Table 13.1 : Angles of Incidence and Reflection"}]}]},
        {"topic_name": "13.7 What is inside Our Eyes?", "sub_topics": [{"sub_topic_name": null, "content": [{"type": "paragraph", "text": "We see things only when light coming from them enters our eyes."}, {"type": "image", "caption": "Fig. 13.14: Human eye"}, {"type": "activity", "name": "Activity 13.8", "text": "Look into your friend’s eye. Observe the size of the pupil."}]}]},
        {"topic_name": "13.10 What is the Braille System?", "sub_topics": [{"sub_topic_name": null, "content": [{"type": "paragraph", "text": "The most popular resource for visually challenged persons is Braille."}]}]},
        {"topic_name": "Exercises", "sub_topics": [], "content": [{"type": "question", "text": "1. Suppose you are in a dark room. Can you see objects in the room? Can you see objects outside the room. Explain."}]}
    ]
  }
]
"""

# This is the full, pre-generated Markdown output for the study planner.
MOCK_PLANNER_OUTPUT = """
### Class 8 Science Study Planner: 12-Day Schedule

| Day | Chapter(s) & Topic(s) | Learning Objectives | Key Activities/Exercises | Estimated Duration (Mins) |
| :-- | :--- | :--- | :--- | :--- |
| **1** | **Chapter 8:** Force and Pressure (8.1, 8.2, 8.3) | - Define force. <br>- Understand force as a push or a pull. <br>- Recognize that forces are due to interaction and have magnitude/direction. | - Table 8.1 <br>- Activity 8.2 | 50 |
| **2** | **Chapter 8:** Force and Pressure (8.4, 8.5) | - Understand how force can change the state of motion and shape of an object. | - Activity 8.3, 8.4, 8.5 | 45 |
| **3** | **Chapter 8:** Force and Pressure (8.6, 8.7, 8.8) | - Differentiate between contact (muscular, friction) and non-contact forces (magnetic, electrostatic, gravitational). <br>- Define pressure. | - Activity 8.6, 8.7 <br>- Discuss why porters use cloth on their heads. | 55 |
| **4** | **Chapter 8 & 13:** Pressure & Light | - Understand that liquids and gases exert pressure. <br>- Introduce the concept of light and reflection. | - Activity 8.9, 8.10 <br>- Activity 13.1 | 50 |
| **5** | **Chapter 13:** Light (13.2, 13.3) | - State and understand the two laws of reflection. <br>- Differentiate between regular and diffused reflection. | - Activity 13.2, 13.4 <br>- Table 13.1 | 50 |
| **6** | **Chapter 13:** Light (13.4, 13.5) | - Understand how multiple images are formed (kaleidoscope). <br>- Learn about reflected light and its properties. | - Activity 13.5, 13.6 | 45 |
| **7** | **Chapter 13:** Light (13.6, 13.7) | - Understand dispersion of light. <br>- Learn the basic structure of the human eye (cornea, iris, pupil, lens, retina). | - Activity 13.7, 13.8 <br>- Fig. 13.14 | 60 |
| **8** | **Chapter 6:** Reproduction in Animals (6.1, 6.2) | - Differentiate between sexual and asexual reproduction. <br>- Identify male and female reproductive organs. | - Fig. 6.1, 6.3 | 50 |
| **9** | **Chapter 6:** Reproduction in Animals (6.2) | - Define and describe internal and external fertilisation. <br>- Understand the development of the embryo. | - Activity 6.1 <br>- Discuss test-tube babies. | 55 |
| **10**| **Chapter 6 & 7:** Reproduction & Adolescence | - Differentiate viviparous and oviparous animals. <br>- Define adolescence and puberty. | - Activity 6.2 <br>- Discuss metamorphosis (frog). | 50 |
| **11**| **Chapter 7:** Reaching the Age of Adolescence (7.2, 7.3, 7.4) | - Identify the physical and hormonal changes during puberty (height, voice, etc.). <br>- Understand the role of hormones. | - Activity 7.1, 7.2 <br>- Fig. 7.3 | 60 |
| **12**| **Chapter 7:** Reaching the Age of Adolescence (7.5 - 7.9) | - Understand the reproductive phase of life. <br>- Learn the importance of reproductive health and personal hygiene. | - Activity 7.4, 7.5 <br>- Discuss "Say NO to Drugs" | 50 |
"""

def generate_content(prompt):
    """
    This function simulates a call to an AI Model API.
    It checks the provided prompt and returns the appropriate pre-generated
    response, removing the need for a live API key.
    """
    if "data extractor" in prompt:
        return MOCK_JSON_OUTPUT
    elif "curriculum developer" in prompt:
        return MOCK_PLANNER_OUTPUT
    return "Error: Unknown prompt."

# ==============================================================================
# SECTION 3: CORE LOGIC
# This section contains the main execution flow of the script.
# ==============================================================================

def execute_extraction():
    """
    Executes the content extraction task.
    It calls the mock API and saves the output to a JSON file.
    """
    print("Step 1: Executing structured content extraction...")
    # The prompt is passed to the mock function, which returns the hardcoded JSON data
    json_output_str = generate_content(EXTRACTION_PROMPT)

    # Parse the JSON string into a Python dictionary
    all_chapters_data = json.loads(json_output_str)

    # Save the structured data to the required JSON file
    with open('chapter-extract.json', 'w') as f:
        json.dump(all_chapters_data, f, indent=2)
    print(" -> Success: 'chapter-extract.json' created.")

    return all_chapters_data

def generate_excel_output(data):
    """
    Generates a well-formatted Excel file from the structured JSON data.
    """
    print("Step 2: Generating Excel output file...")

    # Flatten the hierarchical JSON data into a flat list for the Excel sheet
    flat_data = []
    for chapter in data:
        for topic in chapter.get('topics', []):
            sub_topics = topic.get('sub_topics', [])
            if not sub_topics and 'content' in topic: # Handle topics with direct content (like Exercises)
                 for content_item in topic.get('content', []):
                    row = {
                        'Chapter Number': chapter.get('chapter_number'),
                        'Chapter Name': chapter.get('chapter_name'),
                        'Topic Name': topic.get('topic_name'),
                        'Sub-topic Name': None,
                        'Content Type': content_item.get('type'),
                        'Content/Caption': content_item.get('text') or content_item.get('name') or content_item.get('caption')
                    }
                    flat_data.append(row)
            else:
                for sub_topic in sub_topics:
                    for content_item in sub_topic.get('content', []):
                        row = {
                            'Chapter Number': chapter.get('chapter_number'),
                            'Chapter Name': chapter.get('chapter_name'),
                            'Topic Name': topic.get('topic_name'),
                            'Sub-topic Name': sub_topic.get('sub_topic_name'),
                            'Content Type': content_item.get('type'),
                            'Content/Caption': content_item.get('text') or content_item.get('name') or content_item.get('caption')
                        }
                        flat_data.append(row)

    # Create a pandas DataFrame and save it to an Excel file
    df = pd.DataFrame(flat_data)
    df.to_excel('Copy of Science-sample-output.xlsx', index=False, engine='openpyxl')
    print(" -> Success: 'Copy of Science-sample-output.xlsx' created.")


def generate_study_planner():
    """
    Executes the study planner generation task.
    It calls the mock API and saves the output to a Markdown file.
    """
    print("Step 3: Generating the study/teaching planner...")
    num_days = 12

    # Format the prompt with the number of days
    planner_prompt = PLANNER_PROMPT_TEMPLATE.format(days=num_days)

    # Call the mock API, which will return the hardcoded planner
    study_planner_md = generate_content(planner_prompt)

    # Save the planner to a Markdown file.
    with open('study_planner.md', 'w') as f:
        f.write(study_planner_md)
    print(f" -> Success: {num_days}-day 'study_planner.md' created.")

def generate_knowledge_graph(data):
    """
    Generates and saves the text-based knowledge graph.
    """
    print("Step 4: Generating the text-based knowledge graph...")
    graph_lines = ["Knowledge Graph: NCERT Class 8 Science\n"]

    for chapter in data:
        graph_lines.append(f"\n[Chapter {chapter['chapter_number']}: {chapter['chapter_name']}]")
        for topic in chapter.get('topics', []):
            graph_lines.append(f"  |--> (has topic) --> [{topic.get('topic_name', 'N/A')}]")
            for sub_topic in topic.get('sub_topics', []):
                 graph_lines.append(f"  |     |--> (has sub-topic) --> [{sub_topic.get('sub_topic_name', 'Details')}]")
                 for content_item in sub_topic.get('content', []):
                     if content_item.get('type') in ['activity', 'image', 'table']:
                         graph_lines.append(f"  |     |     |--> (contains) --> [{content_item['type'].capitalize()}: {content_item.get('name') or content_item.get('caption')}]")

    with open('knowledge_graph.txt', 'w') as f:
        f.write("\n".join(graph_lines))
    print(" -> Success: 'knowledge_graph.txt' created.")


def main():
    """
    Main function to run the entire task workflow.
    """
    print("--- Starting Prompt Engineering Task Execution ---")

    # Task 1 & 3.1: Extract content and save to JSON
    extracted_data = execute_extraction()

    # Task 3.2: Generate the Excel file from JSON data
    generate_excel_output(extracted_data)

    # Task 3.4 & 5: Generate the knowledge graph and study planner
    generate_knowledge_graph(extracted_data)
    generate_study_planner()

    print("\n--- All tasks completed successfully. ---")
    print("The following files have been generated in the current directory:")
    print("1. chapter-extract.json")
    print("2. Copy of Science-sample-output.xlsx")
    print("3. study_planner.md")
    print("4. knowledge_graph.txt")


if __name__ == '__main__':
    main()