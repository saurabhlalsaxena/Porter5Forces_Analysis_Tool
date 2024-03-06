import streamlit as st
import os
import modal

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
        doc = open("Michael Porter's paper on 5 forces analysis.txt", 'r')
        f = modal.Function.lookup("porter-five-forces-project", "process_crew")
        result = f.remote(industry_name,doc)
      st.write(result)

if __name__ == "__main__":
    main()
