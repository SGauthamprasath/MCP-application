import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000", // FastAPI backend
});

export const sendMessage = async (message) => {
  const response = await API.post("/chat", {
    message: message,
  });
  return response.data;
};