import psutil
import openai

# Set your OpenAI API key
openai.api_key = "your-openai-api-key"

def monitor_system():
    """Monitor system activity and return data."""
    return {
        "cpu_usage": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory()._asdict(),
        "disk": psutil.disk_usage('/')._asdict(),
        "network": psutil.net_io_counters()._asdict(),
    }

def detect_threat(system_data):
    """Use ChatGPT to detect threats from system data."""
    prompt = f"Analyze the following system data and detect potential threats:\n{system_data}"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

def generate_recommendation(threat_description):
    """Generate recommendations to fix detected threats."""
    prompt = f"Provide recommendations to fix the following threat:\n{threat_description}"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()