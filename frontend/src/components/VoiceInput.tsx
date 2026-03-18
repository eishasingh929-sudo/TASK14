import { Mic } from "lucide-react";

interface Props {
  isRecording: boolean;
  onToggle: () => void;
}

export function VoiceInput({ isRecording, onToggle }: Props) {
  return (
    <button type="button" onClick={onToggle} title="Voice input">
      <Mic color={isRecording ? "#dc2626" : "#334155"} size={18} />
    </button>
  );
}
