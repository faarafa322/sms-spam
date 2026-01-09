# SMS Spam Classification (Training + FastAPI Deploy)

## 1) Setup
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

## 2) Get dataset (UCI SMS Spam Collection)
```bash
python train/download_dataset.py
```
This will create: `train/sms_spam.csv`

## 3) Train + Evaluate + Heatmap
```bash
python train/train.py
```
Outputs:
- `train/metrics_heatmap.png`
- `app/vectorizer.pkl`
- `app/model.pkl`

## 4) Run API locally
```bash
cd app
uvicorn main:app --reload
```
Open docs: http://127.0.0.1:8000/docs

Example request:
```bash
curl -X POST "http://127.0.0.1:8000/predict" ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"Free entry in a weekly competition. Text WIN to 80086\"}"
```

## 5) Deploy (Render example)
Build Command:
```
pip install -r requirements.txt
```
Start Command:
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
