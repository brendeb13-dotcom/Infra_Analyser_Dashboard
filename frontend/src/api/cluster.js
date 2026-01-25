import axios from "axios";

const API_BASE = "http://localhost:8000/api/v1";

export const fetchClusterOverview = async (client, env) => {
  const res = await axios.get(
    `${API_BASE}/cluster/overview`,
    { params: { client_id: client, environment: env } }
  );
  return res.data;
};

export const fetchClusterDetails = async (name, client, env) => {
  const res = await axios.get(
    `${API_BASE}/cluster/${name}`,
    { params: { client_id: client, environment: env } }
  );
  return res.data;
};
