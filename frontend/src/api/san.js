import axios from "axios";

const API = "http://localhost:8000";

export const fetchSanOverview = (client, env) =>
  axios
    .get(`${API}/api/v1/san/overview`, {
      params: { client_id: client, environment: env },
    })
    .then((res) => res.data);
