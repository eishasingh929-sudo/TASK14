import { ReasoningTrace } from "./ReasoningTrace";
import { VerificationBadge } from "./VerificationBadge";
import { UniGuruResponse } from "../types/uniguru";

interface Props {
  role: "user" | "assistant";
  content: string;
  payload?: UniGuruResponse;
}

export function MessageBubble({ role, content, payload }: Props) {
  return (
    <div className={`bubble ${role}`}>
      <div>{content}</div>
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
