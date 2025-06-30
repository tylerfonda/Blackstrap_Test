from openai import OpenAI
import json
import os
import logging
from typing import List, Dict, Optional
from ..db.models import Database, Narrative, Article, MCPEntry

class SynthesizerAgent:
    """
    The Synthesizer Agent takes articles and creates narrative summaries using LLM.
    It also updates the Master Context Profile with new insights.
    """
    
    def __init__(self):
        self.db = Database()
        # Set up OpenAI client - will use environment variable OPENAI_API_KEY
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable is required but not set")
        
        self.client = OpenAI(api_key=api_key)
        logging.info("SynthesizerAgent initialized with OpenAI client")
    
    def synthesize_narrative(self, feed_id: str, topic: str, guidance: str = "") -> str:
        """
        Main entry point: synthesize articles into a narrative for a feed.
        Returns narrative ID.
        """
        logging.info(f"Starting narrative synthesis for feed {feed_id}, topic: {topic}")
        
        # First, use Seeker to get fresh articles
        from .seeker import SeekerAgent
        seeker = SeekerAgent()
        article_ids = seeker.seek_articles(feed_id, topic)
        logging.info(f"Retrieved {len(article_ids)} articles for synthesis")
        
        # Get article content
        articles = self._get_articles_content(article_ids)
        logging.info(f"Loaded content for {len(articles)} articles")
        
        # Create synthesis prompt
        prompt = self._create_synthesis_prompt(topic, articles, guidance)
        
        # Generate narrative using OpenAI
        narrative_content = self._generate_with_openai(prompt)
        
        # Create title from first line of content
        lines = narrative_content.split('\n')
        title = lines[0].replace('# ', '').strip() if lines else "Untitled Narrative"
        content = '\n'.join(lines[1:]).strip() if len(lines) > 1 else narrative_content
        
        # Save narrative
        narrative_id = Narrative.create(feed_id, title, content, article_ids)
        logging.info(f"Created narrative {narrative_id} with title: {title}")
        
        # Update MCP with new insights
        self._update_mcp(narrative_content, topic)
        
        return narrative_id
    
    def _get_articles_content(self, article_ids: List[str]) -> List[Dict]:
        """Get full article content for synthesis"""
        conn = self.db.get_connection()
        articles = []
        
        for article_id in article_ids:
            row = conn.execute(
                'SELECT title, abstract, authors, url FROM articles WHERE id = ?',
                (article_id,)
            ).fetchone()
            
            if row:
                articles.append({
                    'title': row['title'],
                    'abstract': row['abstract'],
                    'authors': json.loads(row['authors']) if row['authors'] else [],
                    'url': row['url']
                })
        
        conn.close()
        return articles
    
    def _create_synthesis_prompt(self, topic: str, articles: List[Dict], guidance: str) -> str:
        """Create the synthesis prompt for OpenAI"""
        articles_text = ""
        for i, article in enumerate(articles, 1):
            authors_str = ", ".join(article['authors']) if article['authors'] else "Unknown"
            articles_text += f"\n\n--- Article {i} ---\n"
            articles_text += f"Title: {article['title']}\n"
            articles_text += f"Authors: {authors_str}\n"
            articles_text += f"Abstract: {article['abstract']}\n"
            if article['url']:
                articles_text += f"URL: {article['url']}\n"
        
        guidance_text = f"\n\nSynthesis guidance: {guidance}" if guidance else ""
        
        return f"""You are a contemplative academic synthesizer. Create a thoughtful narrative that weaves together insights from these research articles about {topic}.

Your narrative should:
- Begin with a compelling title (start with #)
- Synthesize themes and connections across the articles
- Highlight practical implications and future directions
- Be written in a contemplative, readable style that invites deep thinking
- Include relevant citations and links where appropriate
- Be substantive but not overwhelming (aim for 800-1200 words)

Articles to synthesize:{articles_text}{guidance_text}

Create a narrative that helps readers understand the current state and future possibilities in this field:"""
    
    def _generate_with_openai(self, prompt: str) -> str:
        """Generate narrative using OpenAI GPT"""
        logging.info("Sending request to OpenAI API")
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a thoughtful academic writer who creates contemplative, well-structured narratives."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            content = response.choices[0].message.content.strip()
            logging.info(f"OpenAI API request successful, generated {len(content)} characters")
            return content
        except Exception as e:
            logging.error(f"OpenAI API request failed: {type(e).__name__}: {str(e)}")
            # Fallback content if OpenAI fails
            return f"""# Synthesis Pending
            
The Synthesizer encountered an issue generating content: {str(e)}

Please check your OpenAI API key configuration. In the meantime, here's a placeholder narrative about the gathered research.

This synthesis would normally weave together insights from the collected articles, highlighting key themes, practical applications, and future research directions in a contemplative format that invites deep reading and reflection.

*Note: Set your OPENAI_API_KEY environment variable to enable full synthesis capabilities.*"""
    
    def _update_mcp(self, narrative_content: str, topic: str):
        """Update Master Context Profile with new insights"""
        # For now, just store the narrative text
        # Later we can add embedding generation and more sophisticated context tracking
        MCPEntry.create(
            content_type="narrative",
            content_text=narrative_content,
            metadata={"topic": topic}
        )
        logging.info("Updated Master Context Profile with new narrative")

