from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import uuid
import os
from dotenv import load_dotenv
from .db.models import Database, Feed, Article, Narrative, MCPEntry

def create_app():
    # Load environment variables from .env file
    load_dotenv()
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Initialize database
    Database()
    
    @app.route('/')
    def index():
        """Main dashboard showing feeds and recent narratives"""
        feeds = Feed.get_all()
        return render_template('index.html', feeds=feeds)
    
    @app.route('/feeds')
    def feeds():
        """Feed management page"""
        feeds = Feed.get_all()
        return render_template('feeds.html', feeds=feeds)
    
    @app.route('/feeds/new', methods=['GET', 'POST'])
    def new_feed():
        """Create a new feed"""
        if request.method == 'POST':
            name = request.form.get('name')
            topic = request.form.get('topic')
            guidance = request.form.get('guidance', '')
            sources = request.form.getlist('sources')
            
            if name and topic:
                feed_id = Feed.create(name, topic, guidance, sources)
                flash(f'Feed "{name}" created successfully!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Name and topic are required.', 'error')
        
        return render_template('new_feed.html')
    
    @app.route('/narratives/<feed_id>')
    def narratives(feed_id):
        """View narratives for a specific feed"""
        narratives = Narrative.get_by_feed(feed_id)
        return render_template('narratives.html', narratives=narratives, feed_id=feed_id)
    
    @app.route('/synthesize/<feed_id>', methods=['POST'])
    def synthesize(feed_id):
        """Trigger synthesis for a feed"""
        try:
            # Get feed details
            conn = Database().get_connection()
            feed_row = conn.execute('SELECT name, topic, guidance FROM feeds WHERE id = ?', (feed_id,)).fetchone()
            conn.close()
            
            if feed_row:
                app.logger.info(f"Starting synthesis for feed {feed_id}: {feed_row['topic']}")
                from .agents.synthesizer import SynthesizerAgent
                synthesizer = SynthesizerAgent()
                narrative_id = synthesizer.synthesize_narrative(feed_id, feed_row['topic'], feed_row['guidance'] or "")
                app.logger.info(f"Synthesis completed successfully. Narrative ID: {narrative_id}")
                flash('New narrative synthesized successfully!', 'success')
            else:
                app.logger.warning(f"Feed not found: {feed_id}")
                flash('Feed not found', 'error')
        except Exception as e:
            app.logger.exception(f"Synthesis failed for feed {feed_id}")
            flash(f'Synthesis failed: {str(e)}', 'error')
        
        return redirect(url_for('narratives', feed_id=feed_id))

    @app.route('/feedback/<narrative_id>', methods=['POST'])
    def feedback(narrative_id):
        """Save user feedback on narratives"""
        notes = request.form.get('notes', '')
        rating = request.form.get('rating')
        
        if notes or rating:
            from .db.models import Database
            conn = Database().get_connection()
            conn.execute('''
                INSERT INTO feedback (id, narrative_id, notes, rating)
                VALUES (?, ?, ?, ?)
            ''', (str(uuid.uuid4()), narrative_id, notes, int(rating) if rating else None))
            conn.commit()
            conn.close()
            flash('Thank you for your feedback!', 'success')
        
        # Redirect back to narratives page
        conn = Database().get_connection()
        narrative_row = conn.execute('SELECT feed_id FROM narratives WHERE id = ?', (narrative_id,)).fetchone()
        conn.close()
        
        if narrative_row:
            return redirect(url_for('narratives', feed_id=narrative_row['feed_id']))
        else:
            return redirect(url_for('index'))

    return app


# Create the app instance for import
app = create_app()
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)

