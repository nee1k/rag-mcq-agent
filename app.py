import streamlit as st
import pandas as pd
import csv
import os
import sys
from io import StringIO
from datetime import datetime

# Add parent directory to path to import agent modules
sys.path.insert(0, os.path.dirname(__file__))
from agent.hip_agent import HIPAgent

# Page configuration
st.set_page_config(
    page_title="Hippocratic AI | MCQ Agent",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimal CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Header
st.title("Hippocratic AI MCQ Agent")
st.caption("Multiple Choice Question Evaluation powered by RAG & GPT-3.5")

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'processing_time' not in st.session_state:
    st.session_state.processing_time = None

def process_questions(data, headers):
    """Process questions and return results."""
    if st.session_state.agent is None:
        st.session_state.agent = HIPAgent()
    
    agent = st.session_state.agent
    results = []
    progress_bar = st.progress(0)
    
    for idx, row in enumerate(data):
        progress_bar.progress((idx + 1) / len(data))
        
        question_id = row[headers.index("id")]
        question = row[headers.index("question")]
        answer_choices = [
            row[headers.index("answer_0")],
            row[headers.index("answer_1")],
            row[headers.index("answer_2")],
            row[headers.index("answer_3")]
        ]
        correct_answer_text = row[headers.index("correct")]
        correct_answer_idx = answer_choices.index(correct_answer_text)
        response_idx = agent.get_response(question, answer_choices)
        is_correct = response_idx == correct_answer_idx
        
        results.append({
            'id': question_id,
            'question': question,
            'answer_choices': answer_choices,
            'agent_response_idx': response_idx,
            'agent_response_text': answer_choices[response_idx] if 0 <= response_idx < len(answer_choices) else "Invalid response",
            'correct_answer_idx': correct_answer_idx,
            'correct_answer_text': correct_answer_text,
            'is_correct': is_correct
        })
    
    progress_bar.empty()
    return results

# Sidebar
with st.sidebar:
    st.header("Upload CSV")
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    
    if uploaded_file is not None:
        if st.button("Process Questions", type="primary", use_container_width=True):
            start_time = datetime.now()
            with st.spinner("Processing..."):
                try:
                    content = uploaded_file.getvalue().decode('utf-8')
                    csv_file = StringIO(content)
                    reader = csv.reader(csv_file, delimiter=",")
                    headers = next(reader)
                    data = list(reader)
                    
                    results = process_questions(data, headers)
                    
                    end_time = datetime.now()
                    st.session_state.processing_time = (end_time - start_time).total_seconds()
                    st.session_state.results = results
                    st.success(f"Processed {len(data)} questions")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    st.divider()
    
    # Quick start
    default_file_path = os.path.join(os.path.dirname(__file__), 'data', 'testbench.csv')
    if os.path.exists(default_file_path):
        if st.button("Use Default Testbench", use_container_width=True):
            start_time = datetime.now()
            with st.spinner("Processing..."):
                try:
                    with open(default_file_path, 'r') as csvfile:
                        reader = csv.reader(csvfile, delimiter=",")
                        headers = next(reader)
                        data = list(reader)
                    
                    results = process_questions(data, headers)
                    
                    end_time = datetime.now()
                    st.session_state.processing_time = (end_time - start_time).total_seconds()
                    st.session_state.results = results
                    st.success(f"Processed {len(data)} questions")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    st.divider()
    
    with st.expander("CSV Format"):
        st.markdown("""
        Required columns:
        - id, question, answer_0, answer_1, answer_2, answer_3, correct
        
        Example:
        ```csv
        id,question,answer_0,answer_1,answer_2,answer_3,correct
        1,"Question?","A","B","C","D","B"
        ```
        """)

# Main content area
if st.session_state.results is not None:
    results = st.session_state.results

    # Calculate metrics
    total_questions = len(results)
    correct_answers = sum(1 for r in results if r['is_correct'])
    score_percentage = (correct_answers / total_questions) * 100
    processing_time = st.session_state.processing_time or 0

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total", total_questions)
    col2.metric("Correct", correct_answers)
    col3.metric("Accuracy", f"{score_percentage:.1f}%")
    col4.metric("Time", f"{processing_time:.1f}s")

    st.divider()

    # Question analysis
    col_filter1, col_filter2 = st.columns([3, 1])
    
    with col_filter1:
        show_filter = st.selectbox("Filter:", ["All", "Correct Only", "Incorrect Only"])
    
    with col_filter2:
        df = pd.DataFrame([{
            'Question ID': r['id'],
            'Question': r['question'],
            'Agent Response': r['agent_response_text'],
            'Correct Answer': r['correct_answer_text'],
            'Is Correct': r['is_correct']
        } for r in results])
        csv_export = df.to_csv(index=False)
        st.download_button(
            "Download CSV",
            data=csv_export,
            file_name=f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    # Display results
    filtered_results = results
    if show_filter == "Correct Only":
        filtered_results = [r for r in results if r['is_correct']]
    elif show_filter == "Incorrect Only":
        filtered_results = [r for r in results if not r['is_correct']]

    for result in filtered_results:
        status_icon = "✓" if result['is_correct'] else "✗"
        
        with st.expander(f"{status_icon} Question {result['id']}: {result['question'][:60]}{'...' if len(result['question']) > 60 else ''}"):
            st.write(f"**Question:** {result['question']}")
            st.write("**Choices:**")
            
            for idx_choice, choice in enumerate(result['answer_choices']):
                if idx_choice == result['agent_response_idx'] and idx_choice == result['correct_answer_idx']:
                    st.success(f"{idx_choice}. {choice}")
                elif idx_choice == result['agent_response_idx']:
                    st.error(f"{idx_choice}. {choice}")
                elif idx_choice == result['correct_answer_idx']:
                    st.info(f"{idx_choice}. {choice}")
                else:
                    st.write(f"{idx_choice}. {choice}")

else:
    st.info("Upload a CSV file or use the default testbench to get started.")
