# Hippocratic AI Coding Assignment
Welcome to the [Hippocratic AI](https://www.hippocraticai.com) coding assignment

## Instructions
The attached code is a simple multiple-choice question taker.  We have included sample questions.  Your goal is to make this code "better"
- Do not modify testbench.py
- You may do anything you like inside hip_agent.py (or add more files) as long as the interface to testbench.py remains the same
- You must use GPT 3.5 as the LLM (not gpt 4, or any other model)
- We included an openai api key. Please don't abuse it.
- The starter code is based on version 0.27.8 of the openai SDK (included in requirements.txt)

---

## Rules
- This assignment is open-ended. Part of the test is seeing what you decide is important.
- You may use any resources you like with the following restrictions
   - They must be resources that would be available to you if you worked here (so no other humans, no closed AIs, no unlicensed code, etc.)
   - Allowed resources include but not limited to Stack overflow, random blogs, Chatgpt et al. 
   - Please don't use the LangChain or a similar library (openai client library is allowed to make llm calls). We want to see you code.
- DO NOT PUSH THE API KEY TO GITHUB. OpenAI will automatically delete it.
- You may ask questions.

---

## What does "Better" mean

*You* decide what better means, but here are some ideas to help get the brain-juices flowing!

- Improve the score using various well-studied methods
  - Shots
  - Chain of thought
  - Introduce documents and retrieval augmented generation (we included one open source book, but you are welcome to add whatever you like)
    - The entire book will not fit in GPT 3.5 context window
    - Read up on embeddings and cosine similarity here https://platform.openai.com/docs/guides/embeddings
    - There is no need to use a vector db
  - Web search engine integration
- Add a front end interface
- Add testbenches

---

## How will I be evaluated
Good question. We want to know the following
- Can you code
- Can you understand and deconstruct a problem
- Can you operate in an open-ended environment
- Can you be creative
- Do you understand what it means to deliver value versus check a box
- Can you *really* code
- Can you surprise us
