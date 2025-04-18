from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "online", "service": "AI Phone Service Backend"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/twilio/webhook")
def twilio_webhook():
    return {"message": "Twilio webhook endpoint"}

@app.get("/api/calendar/availability")
def calendar_availability():
    return {"message": "Calendar availability endpoint"}


