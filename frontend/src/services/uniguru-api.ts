import axios from "axios";
import { UniGuruResponse } from "../types/uniguru";

const BASE = import.meta.env.VITE_UNIGURU_API_URL || "http://localhost:8000";
const TOKEN = import.meta.env.VITE_UNIGURU_API_TOKEN || "";

export async function ask(query: string, caller = "uniguru-frontend"): Promise<UniGuruResponse> {
  const response = await axios.post(
    `${BASE}/ask`,
    { query, context: { caller } },
    { headers: { Authorization: `Bearer ${TOKEN}` } }
  );
  return response.data as UniGuruResponse;
}

export async function voiceQuery(audioBlob: Blob): Promise<UniGuruResponse> {
  const response = await axios.post(`${BASE}/voice/query`, audioBlob, {
    headers: {
      Authorization: `Bearer ${TOKEN}`,
      "X-Caller-Name": "uniguru-frontend",
      "content-type": audioBlob.type
    }
  });
  return response.data as UniGuruResponse;
}
