from flask import Flask, render_template, request, flash, redirect, url_for
import subprocess
import os
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Replace with a secure key in production

# Load environment variables
load_dotenv()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        secret = request.form.get('secret') or os.getenv('PETZI_SECRET', 'AEeyJhbGciOiJIUzUxMiIsImlzcyI6')

        if not url:
            flash('Webhook URL is required!', 'danger')
            return redirect(url_for('index'))

        try:
            # Run the simulator script
            result = subprocess.run(
                ['python', 'petzi_simulator.py', url, '--secret', secret],
                capture_output=True,
                text=True,
                check=True
            )
            flash(result.stdout, 'success')
        except subprocess.CalledProcessError as e:
            flash(e.stderr or 'An error occurred while running the simulator.', 'danger')

        return redirect(url_for('index'))

    return render_template('index.html')
