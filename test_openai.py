import os
os.environ['OPENAI_API_KEY'] = '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'

try:
    print("Testing OpenAI integration...")
    from openai import OpenAI
    client = OpenAI()
    print("✓ OpenAI client created successfully")
    
    from app.agents.synthesizer import SynthesizerAgent
    synthesizer = SynthesizerAgent()
    print("✓ SynthesizerAgent imported successfully")
    
    # Test a quick synthesis
    narrative_id = synthesizer.synthesize_narrative('test-feed-id', 'artificial intelligence ethics', 'Focus on responsible AI')
    print(f"✓ Narrative created: {narrative_id}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
