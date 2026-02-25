const knowledgeBase = {
  "what is gravity": {
    answer: "Gravity is a force that pulls objects toward each other.",
    confidence: 0.9,
    source: "textbook"
  },
  "what is sun": {
    answer: "The sun is a star at the center of the solar system.",
    confidence: 0.85,
    source: "textbook"
  }
};
function inputNormalization(input) {
  console.log("➡️ Enter: Input Normalization");

  const normalized = input.trim().toLowerCase();

  console.log("⬅️ Exit: Input Normalization");
  return normalized;
}
function knowledgeLookup(normalizedInput) {
  console.log("➡️ Enter: Knowledge Lookup");

  const data = knowledgeBase[normalizedInput] || null;

  console.log("⬅️ Exit: Knowledge Lookup");
  return data;
}
function validation(data) {
  console.log("➡️ Enter: Validation");

  if (data === null) {
    console.log("❌ Validation failed: No data");
    return false;
  }

  console.log("✅ Validation passed");
  return true;
}
function confidenceEvaluation(data) {
  console.log("➡️ Enter: Confidence Evaluation");

  const isConfident = data.confidence >= 0.7;

  console.log("⬅️ Exit: Confidence Evaluation");
  return isConfident;
}
function classification(isValid, isConfident) {
  console.log("➡️ Enter: Classification");

  if (!isValid || !isConfident) {
    return "REFUSE";
  }

  return "ANSWER";
}
function responseShaping(type, data) {
  console.log("➡️ Enter: Response Shaping");

  if (type === "REFUSE") {
    return "Request cannot be answered.";
  }

  return data.answer;
}
function pipeline(input) {
  const normalized = inputNormalization(input);
  const data = knowledgeLookup(normalized);
  const isValid = validation(data);
  const isConfident = data ? confidenceEvaluation(data) : false;
  const decision = classification(isValid, isConfident);
  const response = responseShaping(decision, data);

  return response;
}
console.log(pipeline(" What is Gravity "));
console.log(pipeline("What is moon"));
