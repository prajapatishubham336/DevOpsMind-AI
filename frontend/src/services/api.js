
import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000";

export const runLogAnalysis = async (
  logs,
  repoContext,
  githubOwner,
  githubRepo,
  appId
) => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/agents/run`,
      {
        task: "Analyze this application error using logs and repository context. Identify the root cause and recommend a fix.",

        logs: logs,

        repo_context: repoContext || "Not provided",

        github_owner: githubOwner || null,

        github_repo: githubRepo || null,

        app_id: appId ? Number(appId) : null
      }
    );

    return response.data;

  } catch (error) {
    console.error(
      "API Error:",
      error.response?.data || error.message
    );

    throw error;
  }
};
