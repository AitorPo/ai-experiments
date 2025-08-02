import gradio as gr
from rag import run_rag
from text_processing import model

def answer_question(q):
    return run_rag(q, model)
    
gr.Interface(fn=answer_question, inputs="text", outputs="text", title="AI PDF Assistant").launch()