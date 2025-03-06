# Office Letter Refinement System

An AI-powered system that refines office letters by improving tone, spelling, grammar, structure, and coherence using CrewAI and multiple specialized agents.

## Features

- Upload office letters in .docx format
- Multi-agent processing pipeline:
  - Grammar & Spelling correction
  - Tone & Clarity enhancement
  - Coherence & Structure improvement
  - Final professional review
- Before/After comparison
- Download refined letters in .docx format

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -e .
   ```
3. Create a `.env` file with your API keys:
   ```
   GOOGLE_API_KEY=your_google_api_key
   ```
4. Run the Streamlit app:
   ```bash
   streamlit run src/app.py
   ```

## Project Structure

```
office-letter-refinement/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── input_agent.py
│   │   ├── grammar_agent.py
│   │   ├── tone_agent.py
│   │   ├── coherence_agent.py
│   │   ├── review_agent.py
│   │   └── output_agent.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── docx_utils.py
│   └── app.py
├── pyproject.toml
├── README.md
└── .env
```

## Usage

1. Open the Streamlit interface in your browser
2. Upload a .docx file containing your office letter
3. Wait for the AI agents to process your document
4. Review the changes and compare versions
5. Download the refined document

## License

MIT
