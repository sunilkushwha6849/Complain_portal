# GrievAI Production — Deploy Guide
## Railway.app pe publish karna — Step by Step

---

## Step 1 — GitHub pe upload karo

1. GitHub.com par jaao → New Repository banao → naam: `grievai-portal`
2. Yeh sab files upload karo:
   - `app.py`
   - `database.py`
   - `ai_engine.py`
   - `otp_service.py`
   - `requirements.txt`
   - `Procfile`
   - `railway.json`
   - `init_db.py`
   - `static/` folder (index.html ke saath)

---

## Step 2 — Railway.app account banao

1. https://railway.app jaao
2. **"Login with GitHub"** click karo
3. GitHub account se login karo (free hai)

---

## Step 3 — New Project banao

1. Railway dashboard mein **"New Project"** click karo
2. **"Deploy from GitHub repo"** select karo
3. `grievai-portal` repo select karo
4. **"Deploy Now"** click karo

---

## Step 4 — PostgreSQL Database add karo

1. Railway project mein **"+ New"** click karo
2. **"Database"** → **"PostgreSQL"** select karo
3. Add ho jaayega — `DATABASE_URL` automatically set ho jaayegi

---

## Step 5 — Environment Variables set karo

Railway project mein **"Variables"** tab mein jaao aur yeh add karo:

```
TWILIO_ACCOUNT_SID    = ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN     = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER   = +1xxxxxxxxxx
SECRET_KEY            = koi-bhi-random-string-yahan-daalo-abcd1234
```

### Twilio credentials kahan milenge:
1. https://twilio.com → Sign up (free trial mein $15 credit milta hai)
2. Console Dashboard → Account SID aur Auth Token copy karo
3. Phone Numbers → Get a Number → ek number lo

---

## Step 6 — Database initialize karo

Railway mein **"Shell"** tab mein jaao aur run karo:
```bash
python init_db.py
```

---

## Step 7 — Deploy complete!

Railway automatically ek URL dega jaise:
```
https://grievai-portal-production.up.railway.app
```

Yahi aapka **live government portal** hai! Isko kisi ko bhi share karo।

---

## Twilio Trial Limitations

Free trial mein:
- Sirf verified numbers pe SMS jaata hai
- $15 credit milta hai (~1000 OTPs)
- Production ke liye paid plan lena padega (~$0.0075/SMS)

---

## Files Structure

```
grievai-portal/
├── app.py              ← Flask server (main)
├── database.py         ← PostgreSQL
├── ai_engine.py        ← AI classifier
├── otp_service.py      ← Twilio OTP
├── init_db.py          ← DB setup (run once)
├── requirements.txt    ← Dependencies
├── Procfile            ← Railway start command
├── railway.json        ← Railway config
└── static/
    └── index.html      ← Frontend
```

---

## Local Testing

```bash
# 1. .env file banao (.env.example copy karke)
cp .env.example .env
# Usme apne Twilio credentials bharo

# 2. Dependencies install
pip install -r requirements.txt

# 3. DB setup (local PostgreSQL chahiye ya Railway DB URL use karo)
python init_db.py

# 4. Server chalao
python app.py
# → http://localhost:8000
```
