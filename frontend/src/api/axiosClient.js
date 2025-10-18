import axios from "axios";

const axiosClient = axios.create({
  baseURL: "http://localhost:8000", // your FastAPI backend
});

export default axiosClient;