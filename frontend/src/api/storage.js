import axios from "axios";

const API_BASE = "http://localhost:8000";

export const fetchStorageOverview = async (clientId, env) => {
  const res = await axios.get(
    `${API_BASE}/api/v1/storage/overview`,
    { params: { client_id: clientId, environment: env } }
  );
  return res.data;
};
