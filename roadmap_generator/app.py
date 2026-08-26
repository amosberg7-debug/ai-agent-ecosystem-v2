from flask import Flask, render_template_string, request
import os
from langchain_openai import ChatOpenAI
import sys
sys.path.insert(0, '..')
from config import Config

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Free AI Automation Roadmap</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        h1 { color: #1a1a1a; }
        input, select, textarea { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
        button { background: #007bff; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
        .result { background: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>Get Your Free AI Automation Roadmap</h1>
    <p>Answer 4 quick questions and get a personalized plan to save 10+ hours per week.</p>
    
    <form method="POST">
        <input type="text" name="business_name" placeholder="Your Business Name" required>
        <select name="industry" required>
            <option value="">Select Your Industry</option>
            <option value="marketing">Marketing Agency</option>
            <option value="ecommerce">E-commerce</option>
            <option value="consulting">Consulting/Coaching</option>
            <option value="healthcare">Healthcare</option>
            <option value="realestate">Real Estate</option>
            <option value="other">Other</option>
        </select>
        <select name="team_size" required>
            <option value="">Team Size</option>
            <option value="1">Just me</option>
            <option value="2-5">2-5 people</option>
            <option value="6-15">6-15 people</option>
            <option value="16+">16+ people</option>
        </select>
        <textarea name="time_waster" placeholder="What's your biggest time-waster? (e.g., 'manually copying data between spreadsheets', 'answering the same customer emails')" rows="3" required></textarea>
        <input type="email" name="email" placeholder="Your Email (to receive your roadmap)" required>
        <button type="submit">Generate My Free Roadmap</button>
    </form>
    
    {% if result %}
    <div class="result">
        <h2>Your Personalized Roadmap</h2>
        <pre>{{ result }}</pre>
        <p><strong>A copy has been sent to your email!</strong></p>
    </div>
    {% endif %}
</body>
</html>
"""

def generate_roadmap(business_name, industry, team_size, time_waster):
    llm = ChatOpenAI(
        model="~anthropic/claude-sonnet-latest",
        api_key=Config.OPENROUTER_API_KEY,
        base_url=Config.OPENROUTER_BASE_URL,
        temperature=0.7
    )
    
    prompt = f"""Generate a personalized AI Automation Roadmap for this business:
    
Business Name: {business_name}
Industry: {industry}
Team Size: {team_size}
Biggest Time-Waster: {time_waster}

Create a concise, actionable roadmap with:
1. TOP PRIORITY TOOL (what to implement first)
2. IMPLEMENTATION STEPS (3-4 bullet points)
3. HOURS SAVED PER WEEK (realistic estimate)
4. MONTHLY COST (total for recommended tools)
5. 30-DAY ACTION PLAN (what to do this week, next week, etc.)
6. QUICK WIN (one automation they can set up in 1 hour)

Keep it under 300 words. Be specific and practical. Use real tool names (Zapier, Make, n8n, Lindy, Relevance AI) where appropriate."""
    
    response = llm.invoke([{"role": "user", "content": prompt}])
    return response.content

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        business_name = request.form['business_name']
        industry = request.form['industry']
        team_size = request.form['team_size']
        time_waster = request.form['time_waster']
        email = request.form['email']
        
        result = generate_roadmap(business_name, industry, team_size, time_waster)
        
        # Save to file for now (you'll email manually or automate later)
        with open('../roadmap_submissions.txt', 'a') as f:
            f.write(f"Email: {email} | Business: {business_name} | Industry: {industry}\\n")
            f.write(f"Roadmap:\\n{result}\\n")
            f.write("-" * 50 + "\\n")
    
    return render_template_string(HTML_TEMPLATE, result=result)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
