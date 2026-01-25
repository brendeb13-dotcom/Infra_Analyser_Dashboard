1. Prerequisites

Linux (Ubuntu / RHEL / CentOS)
Python 3.10+
Node.js 18+
Ansible

sudo apt update
sudo apt install -y python3 python3-venv python3-pip ansible git curl
sudo apt install -y nodejs

2.BACKEND SETUP

cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 - this will start up the backend
curl http://localhost:8000/health

3.FRONTEND SETUP

Open a new terminal:

cd frontend
npm install
npm run dev

Frontend will start at:

http://localhost:5173

4. ANSIBLE

cd ansible

   ansible-playbook -i inventory.ini ansible/linux_discovery.yml \
  -e client_id=demo_client \
  -e env_name=dev \
  -e run_id=run_001

Now the Dashboard will be up and running in the frontend



