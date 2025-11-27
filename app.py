import os
import streamlit as st
from dotenv import load_dotenv

# ==========================
# 🔑 Load Environment Variables
# ==========================
load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if SERPER_API_KEY is None:
    raise ValueError("❌ SERPER_API_KEY is missing in .env")

if GOOGLE_API_KEY is None:
    raise ValueError("❌ GOOGLE_API_KEY is missing in .env")

# ==========================
# 🛠 CrewAI + Tools
# ==========================
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import SerperDevTool

# ==========================
# 🔧 Initialize Search Tool
# ==========================
search_tool = SerperDevTool()

# ==========================
# 🤖 Initialize Gemini LLM (Correct CrewAI version)
# ==========================
llm = LLM(
    model="google/gemini-2.5-flash",  # or gemini-2.0-pro
    api_key=GOOGLE_API_KEY,
    temperature=0.5
)

# ==========================
# 🧠 Create Agents
# ==========================
news_researcher = Agent(
    role="Senior Researcher",
    goal="Discover groundbreaking insights in {topic}",
    verbose=True,
    memory=True,
    backstory=(
        "You explore the latest technological trends and uncover insights "
        "that are crucial for innovation."
    ),
    tools=[search_tool],
    llm=llm,
)

news_writer = Agent(
    role="Tech Writer",
    goal="Create compelling and clear stories about {topic}",
    verbose=True,
    memory=True,
    backstory=(
        "You transform complex research into engaging and easy-to-read "
        "technology articles."
    ),
    tools=[search_tool],
    llm=llm,
)

# ==========================
# 📌 Create Tasks
# ==========================
research_task = Task(
    description=(
        "Research the next big innovation in {topic}. Provide pros, cons, "
        "future opportunities, risks, and market potential."
    ),
    expected_output="A 3-paragraph detailed research summary.",
    tools=[search_tool],
    agent=news_researcher,
)

write_task = Task(
    description=(
        "Write a 4-paragraph engaging markdown article about {topic} "
        "based on the research provided."
    ),
    expected_output="A well-structured markdown article.",
    tools=[search_tool],
    agent=news_writer,
)

# ==========================
# 🧑‍🚀 Create Crew
# ==========================
crew = Crew(
    agents=[news_researcher, news_writer],
    tasks=[research_task, write_task],
    process=Process.sequential,
)

# ==========================
# 🌐 Streamlit UI
# ==========================
st.set_page_config(page_title="CrewAI News Generator", page_icon="📰")

st.title("📰 CrewAI Tech News Generator")
st.write("AI-powered Research + Writing using **Gemini + CrewAI + Serper**")

topic = st.text_input("Enter a topic:", "AI in healthcare")


if st.button("Generate Article"):
    with st.spinner("Running multi-agent workflow..."):
        result = crew.kickoff(inputs={'topic': topic})

    st.success("Article generated successfully!")

    # Extract clean content
    research_summary = result.tasks_output[0].raw
    final_article = result.tasks_output[1].raw

    st.subheader("🔍 Research Summary")
    st.write(research_summary)

    st.subheader("📝 Final Article")
    st.write(final_article)

    st.download_button(
        label="📥 Download Final Article",
        data=final_article,
        file_name="tech_article.md"
    )

    st.download_button(
        label="📥 Download Research Summary",
        data=research_summary,
        file_name="research_summary.md"
    )
