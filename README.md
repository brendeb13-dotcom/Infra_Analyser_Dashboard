Infrastructure Analyzer Dashboard
Local Installation & Testing Guide 
________________________________________
Prerequisites 
OS
•	RHEL / Rocky / CentOS / Oracle Linux / SLES
•	Tested with RHEL 8+
Required Packages
sudo dnf install -y \
  python3 python3-pip python3-virtualenv \
  git nodejs npm \
  ansible curl
Verify versions:
python3 --version   # >= 3.9
ansible --version   # >= 2.12
node --version      # >= 18
npm --version
________________________________________

cd infra-analyzer-dashboard
Folder structure (expected):
infra-analyzer-dashboard/
├── backend/
├── frontend/
├── ansible/
├── wrappers/
│   └── linux/
└── README.md
________________________________________
Backend Setup (FastAPI)
Create Python Virtual Environment
cd backend
python3 -m venv .venv
source .venv/bin/activate

Install Backend Dependencies
fastapi
uvicorn
pydantic
python-dotenv
Install:
pip install -r requirements.txt
Start Backend
python -m uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000
Verify:
curl http://localhost:8000/health
Expected:
{ "status": "up" }
________________________________________
Frontend Setup (React + Vite)
Open new terminal:
cd frontend
npm install
npm run dev
Frontend will start on:
http://<server-ip>:5173
________________________________________
Ansible Discovery Setup 
Navigate to Ansible Folder
cd ansible

Before running discovery:
export CLIENT_ID=demo_client
export ENVIRONMENT=dev
export RUN_ID=run_001
________________________________________
Run End-to-End Discovery
Execute Playbook
Inventory Case 1:
ansible-playbook -i inventory.ini linux_discovery.yml \
  -e client_id=demo_client \
  -e env_name=dev \
  -e run_id=run_001


What This Discovers
✔ Storage (LUNs, capacity, vendors)
✔ SAN (FCAs, zoning, paths)
✔ Cluster + Apps (services, ports)
✔ Sends data to backend APIs automatically
________________________________________
Validate Dashboard (UI)
Open browser:
http://<server-ip>:5173
Check:
•	✅ Storage Overview (KPIs, hosts, LUNs)
•	✅ SAN Overview (FCAs, paths, zoning)
•	✅ Cluster Overview (nodes + apps)
•	✅ Global search
•	✅ Export buttons

