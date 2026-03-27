import { ReasoningTrace } from "./ReasoningTrace";
import { VerificationBadge } from "./VerificationBadge";
import { UniGuruResponse } from "../types/uniguru";

interface Props {
  role: "user" | "assistant";
  content: string;
  payload?: UniGuruResponse;
}

export function MessageBubble({ role, content, payload }: Props) {
  const presentation = payload?.presentation;
  const paragraphs =
    presentation?.paragraphs && presentation.paragraphs.length > 0
      ? presentation.paragraphs
      : [content].filter(Boolean);

  return (
    <div className={`bubble ${role}`}>
      <div className="bubble-content">
        {paragraphs.map((paragraph, index) => (
          <p key={`${role}-paragraph-${index}`} className="bubble-paragraph">
            {paragraph}
          </p>
        ))}
        {role === "assistant" && presentation?.details && (
          <div className="bubble-section">
            <div className="bubble-label">Details</div>
            <p className="bubble-paragraph">{presentation.details}</p>
          </div>
        )}
        {role === "assistant" && presentation?.source && (
          <div className="bubble-section">
            <div className="bubble-label">Source</div>
            <p className="bubble-meta">{presentation.source}</p>
          </div>
        )}
        {role === "assistant" && presentation?.disclaimer && (
          <p className="bubble-note">{presentation.disclaimer}</p>
        )}
      </div>
      {role === "assistant" && (
        <>
          <VerificationBadge
            status={payload?.verification_status}
            domain={payload?.ontology_reference?.domain}
          />
          <ReasoningTrace trace={payload?.reasoning_trace} />
        </>
      )}
    </div>
  );
}
