pip install --q crewai[tools]
import streamlit as st
import os
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAI
from crewai_tools.tools import WebsiteSearchTool, SerperDevTool, FileReadTool
from langsmith import Client
from textwrap import dedent

client = Client()

# Define the function to create a dictionary from Markdown files in a folder
def create_dict_from_markdown_files(folder_path):
    md_files = [f for f in os.listdir(folder_path) if f.endswith('.md')]
    data_dict = {}

    for file_name in md_files:
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'r') as file:
            file_data = file.read()
            industry_name = file_name[:-3]
            # Process the file data as needed
            data_dict[industry_name] = file_data

    return data_dict


def initialise_tools():
  web_search_tool = WebsiteSearchTool()	
  seper_dev_tool = SerperDevTool()
  file_read_tool = FileReadTool(
	  file_path="./Michael Porter's paper on 5 forces analysis.txt",
	  description='A tool to read the paper by Michael Porter on Porters 5 forces. This paper should be used as the basis of the analysis',
  )
  return web_search_tool, seper_dev_tool,file_read_tool


def initialise_agents(web_search_tool, seper_dev_tool,file_read_tool):
  
  llm = ChatOpenAI(model_name="gpt-4-turbo-preview", temperature=0.7)

  paper_summariser_agent = Agent(
      role='Paper Summariser',
			goal="""Read the paper by Michael porter and build a comprehensive summary of Porter's 5 forces so that the analysis 
      can be implemented by the Researcher and the Analyst""",
			tools=[seper_dev_tool,file_read_tool],
			backstory='Expert in reading papers and summarising them so that the analysis and process described in the paper can be implemented',
			verbose=True,
      llm = llm
  )

  research_agent = Agent(
        role='Researcher',
				goal='Use the analysis methodology created by the Paper Summariser to research all the information to complete the analysis',
				tools=[web_search_tool, seper_dev_tool],
				backstory='Expert in scrolling through the internet to find information on a given topic and dissecting complex data. Expert in documentmenting all the information researhed from websites, blogposts and social media.',
				verbose=True,
        llm = llm
  )

  analyst_agent = Agent(
        role='Analyst',
				goal="""Based on the analysis method provided by the Paper Summariser and the research conducted by the researcher, 
        conduct the Porter's 5 Force Analysis and write an strategy analysis document""",
				tools=[seper_dev_tool],
				backstory='Skilled Analyst with an expertise in strategy and an MBA from Harvard Business School. Expert in writing Strategy documents for a Global Think Tank',
				verbose=True,
        llm = llm
  )

  return paper_summariser_agent, research_agent, analyst_agent


def initialise_task(industry_name,paper_summariser_agent, research_agent, analyst_agent):
  summarise_paper_task = Task(
  						description=dedent(f"""\
								Analyze the provided research paper by Michael Porter regarding the 5 strongest forces that impact the profitability in an industry.
                Identify the 5 Forces, what factors effect the 5 forces, what data points can help identify the impact the Forces.
                Create a summary of the paper which focuses on how the analysis should be implemented for a given industry and what information needs to 
                be researched for the analysis.
                Keep the industry : "{industry_name}" provided by the user as point of reference so that any unique factors or data points in the paper
                with regards to the industry can be identifed.
                Include these key pieces of information that pertains to the above industry."""),
						expected_output=dedent("""\
								A comprehensive implementation methodology to conduct the Porter's 5 force analysis for the user specified industry 
                detailing the factors effecting the 5 forces, how the factors should be evaluated and what information is needed to evaluate these factors. 
                Suggestions on incorporating indutry insights from the paper should be included."""),
						agent=paper_summariser_agent
        )
  
  research_task = Task(
  					description=dedent(f"""\
								Based on industry specified "{industry_name}" and the information requirements from the summarise paper task, search the internet 
                for the information and prepare a document with all the information to be passed on to the analyst."""),
						expected_output=dedent("""\
								A document with all the information to conduct the Porter's 5 force analysis. And a list of links to all the websites
                that you have researched"""),
						agent=research_agent
        )
  
  draft_analysis_task = Task(
  					description=dedent(f"""\
								Create a Mckinsey style porter's 5 force analysis for the industry "{industry_name}" using the methodolgy from the paper summariser agent and
                the information gathered by the researcher.
                Stick to the methodology and forces highlighted in the paper. 
                Do not invent new forces.
                The strategic analysis should come up with final recommendations"""),
						expected_output=dedent("""\
								A detailed Porter's 5 forces analysis document for the industry, clearly mentioning each of the 5 forces and their impact on the 
                industry. Also mention the level of impact of each force as High, Medium or Low. There should be consolidated strategy recommendations at the end.
                All the links and references used for the analysis should be mentioned
                Example Output:
                '## **Porter's 5 Forces Analysis for the Fintech Industry** \n\n
                ---
                ###1. **Introduction** \n\n
                The Fintech industry is a vast and dynamic sector... \n\n 
                ###2. **Analysis** \n\n
                #### **Bargaining Power of Suppliers: High** \n\n
                - Technology core providers in the fintech industry wield significant power...\n\n
                ...
                ###3. **Strategy recommendations** \n\n
                Based on the Porter's Five Forces analysis, the following strategic recommendations are proposed...

                ###4. **Conclusion** \n\n
                The Fintech industry is shaped by dynamic forces that demand strategic agility and innovation...

                **References:**
                ...
                """),
						agent=analyst_agent,
            output_file="analysis_doc.md"
        )
  
  return summarise_paper_task,research_task,draft_analysis_task

def onClick(selection_input):
    if selection_input == '0':
        st.session_state['selection'] = None



def main():
  st.set_page_config(page_title = "Porter's 5 Forces Analysis Tool")
  
  #Load markdown documents
  available_analysis_info = create_dict_from_markdown_files('.')

  industry_options = list(available_analysis_info.keys())

  if 'selection' not in st.session_state:
      st.session_state['selection'] = 0

  st.sidebar.header("PORTER's 5 Forces Analysis Tool")
  
  #Selector for pre-processed Porter's 5 force analysis
  st.sidebar.subheader("Check out existing Analysis")
  selected_industry = st.sidebar.selectbox("Select Industry", industry_options,index=st.session_state['selection'])

  #Display selected industry analysis
  if selected_industry:
    st.write(available_analysis_info[selected_industry])

  st.sidebar.subheader("Process new analysis")
  industry_name = st.sidebar.text_input("Enter the name of the industry","E-commerce")
  process_button = st.sidebar.button("Analyze",on_click=onClick, args='0')
  st.sidebar.markdown("**Note**: Analysis can take upto 5 mins, please be patient.")

  if process_button:
      selected_industry= None
      with st.spinner('Wait for it...'):
        web_search_tool, seper_dev_tool,file_read_tool = initialise_tools()
        paper_summariser_agent, research_agent, analyst_agent = initialise_agents(web_search_tool, seper_dev_tool,file_read_tool)
        summarise_paper_task,research_task,draft_analysis_task = initialise_task(industry_name,paper_summariser_agent, research_agent, analyst_agent)
        crew = Crew(
            agents=[paper_summariser_agent, research_agent, analyst_agent],
            tasks=[
                summarise_paper_task,
                research_task,
                draft_analysis_task
            ]
        )
        result = crew.kickoff()
      st.write(result)

if __name__ == "__main__":
    main()
