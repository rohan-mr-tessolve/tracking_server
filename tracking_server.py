from flask import Flask, request, redirect, jsonify
import sqlite3
from datetime import datetime
from curses import COLS
app = Flask(__name__)
CORS(app)
@app.route('/track_click')
def track_click():
    """Handle tracking URL clicks"""
    tracking_id = request.args.get('tracking_id')
    
    if not tracking_id:
        return jsonify({'error': 'No tracking ID provided'}), 400
    
    try:
        conn = sqlite3.connect('leads.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_id, lead_email, message_id, conversation_id
            FROM email_tracking 
            WHERE tracking_id = ? AND button_clicked = 0
        ''', (tracking_id,))
        
        tracking_record = cursor.fetchone()
        
        if tracking_record:
            record_id, user_id, lead_email, message_id, conversation_id = tracking_record
            
            # Update the record to mark as clicked
            cursor.execute('''
                UPDATE email_tracking 
                SET button_clicked = 1, click_timestamp = ?
                WHERE id = ?
            ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), record_id))
            
            # Create a notification
            cursor.execute('''
                INSERT INTO notifications (user_id, lead_email, message, type)
                VALUES (?, ?, ?, ?)
            ''', (user_id, lead_email, f"Lead {lead_email} clicked the tracking button", "button_click"))
            
            conn.commit()
            
            print(f"✅ Tracking click recorded for {lead_email} (tracking_id: {tracking_id})")
            
            # Redirect to a Tessolve page
            return redirect('https://www.tessolve.com/')
        else:
            print(f"⚠️ Tracking ID not found or already clicked: {tracking_id}")
            return redirect('https://www.tessolve.com/')
    
    except Exception as e:
        print(f"❌ Error tracking click: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
    
    finally:
        conn.close()

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Tracking server is running'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
