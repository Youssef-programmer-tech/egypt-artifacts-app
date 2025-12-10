import sys
import os
import threading
from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class EgyptApp(App):
    def build(self):
        self.title = "Egypt Artifacts"
        self.label = Label(text="Starting...", font_size=24)
        threading.Thread(target=self.run_flask, daemon=True).start()
        Clock.schedule_once(self.update_status, 2)
        return self.label
    
    def run_flask(self):
        try:
            from App import app
            app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
        except Exception as e:
            print(f"Error: {e}")
    
    def update_status(self, dt):
        self.label.text = "✅ Server running!\nhttp://localhost:5000"

EgyptApp().run()
