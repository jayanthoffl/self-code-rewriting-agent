import os
from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI
from tools import ReadFileTool, WriteFileTool

# --- THE FIX: Trick CrewAI to ignore missing OpenAI Key ---
os.environ["OPENAI_API_KEY"] = "NA" 

# 1. Setup Gemini
# We use 'gemini-1.5-flash' which is faster/cheaper, or 'gemini-pro'
# In agent.py
llm = ChatGoogleGenerativeAI(
    # model="gemini-2.5-flash",  # <--- CHANGE THIS back to the stable name
    model="gemini-2.0-flash",
    verbose=True,
    temperature=0.5,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
# 2. Define the Agent
developer = Agent(
    role='Senior Python Developer',
    goal='Fix runtime errors in Python code',
    backstory='You are an expert debugger. You analyze error logs and fix the code immediately.',
    tools=[ReadFileTool(), WriteFileTool()],
    llm=llm,
    verbose=True,
    allow_delegation=False # Don't try to hire other agents (saves time/errors)
)

# 3. The Main Function
def fix_code(repo_path: str, error_log: str):
    """
    Spins up the Crew to analyze the error and fix the file.
    """
    
    # We strip the container prefix to help the AI understand
    clean_error_log = error_log.replace("/app/", "")

    fix_task = Task(
        description=f"""
        A Python application has crashed.
        
        TARGET REPOSITORY: {repo_path}
        ERROR LOGS:
        {clean_error_log}
        
        CRITICAL INSTRUCTION: 
        The error logs reference files like '/app/main.py'. 
        IGNORE the '/app/' prefix. 
        You MUST edit the file located inside the 'TARGET REPOSITORY'.
        
        Example: If error is in 'main.py', you must edit '{repo_path}/main.py'.
        
        Your Mission:
        1. Identify the filename causing the crash.
        2. Construct the FULL ABSOLUTE PATH: {repo_path}/<filename>
        3. Read that file.
        4. Fix the code.
        5. Write the fixed code back to the FULL ABSOLUTE PATH.
        """,
        agent=developer,
        expected_output="A fixed Python file written to the specific repository path."
    )

    crew = Crew(
        agents=[developer],
        tasks=[fix_task],
        verbose=True
    )

    result = crew.kickoff()
    return result