import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const getOverview = async (clientId, environment) => {
  const response = await axios.get(`${API_BASE_URL}/api/v1/overview`, {
    params: {
      client_id: clientId,
      environment: environment,
    },
  });
  return response.data;
};

