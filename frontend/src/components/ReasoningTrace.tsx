import { ReasoningTrace as Trace } from "../types/uniguru";

interface Props {
  trace?: Trace;
}

export function ReasoningTrace({ trace }: Props) {
  if (!trace) {
    return null;
  }

  return (
    <div className="trace">
      <div>Confidence: {trace.retrieval_confidence}</div>
      <div>Sources: {(trace.sources_consulted || []).join(", ")}</div>
    </div>
  );
}
