# ULTRA SIMPLE BACKEND DEPLOYMENT

Since the --no-cloud-build flag is not available, try this absolute simplest solution:

## Create a Minimal App Engine App

1. In Cloud Shell, create a new directory and navigate to it:
```bash
mkdir minimal-app
cd minimal-app
```

2. Create a bare minimum main.py:
```bash
cat > main.py << 'EOF'
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'Sloane AI Phone Service Backend is running!'

@app.route('/api/health')
def health():
    return '{"status": "healthy"}'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
EOF
```

3. Create a minimal app.yaml:
```bash
cat > app.yaml << 'EOF'
runtime: python39
EOF
```

4. Create a minimal requirements.txt:
```bash
cat > requirements.txt << 'EOF'
Flask==2.3.3
EOF
```

5. Deploy this minimal app:
```bash
gcloud app deploy
```

This creates the absolute minimum App Engine application that should deploy successfully without any complications.

## If That Still Fails:

There might be an issue with your Google Cloud project. Try:

1. Check your billing is enabled:
```bash
gcloud billing projects describe clean-code-app-1744825963
```

2. Make sure App Engine API is enabled:
```bash
gcloud services enable appengine.googleapis.com
```

3. Verify you have permission to deploy:
```bash
gcloud projects get-iam-policy clean-code-app-1744825963
```

4. Try creating a new project if necessary.