// Show loader and log message
function logAndShowLoader(message) {
  console.log(">>> " + message);
  const loader = document.getElementById("loader");
  if (loader) {
    loader.classList.remove("d-none");
    console.log("Loader displayed on the page.");
  }
}

// Log MCP server start
function logMCPServer(pid) {
  console.log(`MCP Server started successfully with PID: ${pid}`);
}

// Log question submission
function logQuestionSubmission(question, repo) {
  console.log("Submitting question to MCP server...");
  console.log(`Question: ${question}`);
  console.log(`GitHub Repo: ${repo}`);
}

// Log answer received
function logAnswerReceived(answer) {
  console.log("Answer received from MCP server:");
  console.log(answer);
}

// Example: log session history
function logHistory(history) {
  console.log("Current conversation history:");
  console.table(history);
}

// Auto-scroll console is no longer needed as browser console handles it.
