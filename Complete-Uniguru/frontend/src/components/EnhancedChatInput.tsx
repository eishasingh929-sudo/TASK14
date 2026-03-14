import React, { useEffect, useRef, useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faArrowUp,
  faCompress,
  faCopy,
  faExpand,
  faFile,
  faFilePdf,
  faMicrophone,
  faPaperclip,
  faTimes
} from "@fortawesome/free-solid-svg-icons";
import { gsap } from "gsap";
import toast from "react-hot-toast";

import BubblyButton from "./BubblyButton";
import { sendVoiceQuery } from "../helpers/api-communicator";

interface FileAttachment {
  id: string;
  file: File;
  type: "image" | "pdf" | "document";
  preview?: string;
}

interface EnhancedChatInputProps {
  message: string;
  setMessage: (message: string) => void;
  onSendMessage: () => void;
  onKeyDown: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void;
  textareaRef: React.RefObject<HTMLTextAreaElement>;
  onFileUpload?: (file: File) => void;
  attachments?: FileAttachment[];
  onRemoveAttachment?: (id: string) => void;
}

const placeholderTexts = [
  "Type a message...",
  "Ask me anything...",
  "What can I help you with?",
  "Start a conversation...",
  "Share your thoughts..."
];

const languageOptions = [
  { value: "en-US", label: "EN" },
  { value: "hi-IN", label: "HI" },
  { value: "mr-IN", label: "MR" },
  { value: "ta-IN", label: "TA" },
  { value: "te-IN", label: "TE" },
  { value: "kn-IN", label: "KN" },
  { value: "bn-IN", label: "BN" }
];

const EnhancedChatInput: React.FC<EnhancedChatInputProps> = ({
  message,
  setMessage,
  onSendMessage,
  onKeyDown,
  textareaRef,
  onFileUpload,
  attachments = [],
  onRemoveAttachment
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [showPlaceholder, setShowPlaceholder] = useState(true);
  const [showStats, setShowStats] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const [showSpeechBadge, setShowSpeechBadge] = useState(false);
  const [currentLanguage, setCurrentLanguage] = useState("en-US");
  const [currentPlaceholderIndex, setCurrentPlaceholderIndex] = useState(0);
  const [currentText, setCurrentText] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);

  const containerRef = useRef<HTMLDivElement>(null);
  const placeholderRef = useRef<HTMLSpanElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout>();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const activeStreamRef = useRef<MediaStream | null>(null);

  const charCount = message.length;
  const wordCount = message.trim() ? message.trim().split(/\s+/).length : 0;
  const maxChars = 2000;

  const stopActiveStream = () => {
    if (activeStreamRef.current) {
      activeStreamRef.current.getTracks().forEach((track) => track.stop());
      activeStreamRef.current = null;
    }
  };

  useEffect(() => {
    return () => {
      stopActiveStream();
    };
  }, []);

  useEffect(() => {
    if (!showPlaceholder) {
      return;
    }

    const currentFullText = placeholderTexts[currentPlaceholderIndex];
    const typingSpeed = isDeleting ? 50 : 100;
    const pauseTime = isDeleting ? 500 : 2000;

    const timeout = setTimeout(() => {
      if (!isDeleting) {
        if (currentText.length < currentFullText.length) {
          setCurrentText(currentFullText.slice(0, currentText.length + 1));
        } else {
          setTimeout(() => setIsDeleting(true), pauseTime);
        }
      } else if (currentText.length > 0) {
        setCurrentText(currentText.slice(0, -1));
      } else {
        setIsDeleting(false);
        setCurrentPlaceholderIndex((previous) => (previous + 1) % placeholderTexts.length);
      }
    }, typingSpeed);

    return () => clearTimeout(timeout);
  }, [currentPlaceholderIndex, currentText, isDeleting, showPlaceholder]);

  const handleCopyText = async () => {
    if (!message.trim()) {
      return;
    }
    try {
      await navigator.clipboard.writeText(message);
    } catch (error) {
      console.error("Failed to copy text:", error);
      const textArea = document.createElement("textarea");
      textArea.value = message;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand("copy");
      document.body.removeChild(textArea);
    }
    toast.success("Text copied to clipboard!", { duration: 2000, icon: "Copy" });
  };

  const handleFileClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && onFileUpload) {
      onFileUpload(file);
    }
    event.target.value = "";
  };

  const mapLanguageCode = (languageCode: string) => languageCode.split("-")[0].toLowerCase();

  const startRecording = async () => {
    try {
      if (navigator.permissions?.query) {
        const permissionStatus = await navigator.permissions.query({ name: "microphone" as PermissionName });
        if (permissionStatus.state === "denied") {
          toast.error("Microphone access denied. Please allow microphone access in your browser settings.", {
            duration: 5000,
            icon: "X"
          });
          return;
        }
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });
      activeStreamRef.current = stream;

      const supportedMimeType = [
        "audio/webm;codecs=opus",
        "audio/webm",
        "audio/ogg;codecs=opus",
        "audio/ogg"
      ].find((mimeType) => MediaRecorder.isTypeSupported(mimeType));

      const mediaRecorder = supportedMimeType
        ? new MediaRecorder(stream, { mimeType: supportedMimeType })
        : new MediaRecorder(stream);

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        try {
          const mimeType = mediaRecorder.mimeType || supportedMimeType || "audio/webm";
          const extension = mimeType.includes("ogg") ? "ogg" : "webm";
          const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });

          if (!audioBlob.size) {
            toast.error("No audio captured. Please try again.", { duration: 4000, icon: "X" });
            return;
          }

          toast.loading("Transcribing voice query...", { id: "voice-upload" });
          const voiceResponse = await sendVoiceQuery(audioBlob, {
            caller: "uniguru-frontend",
            language: mapLanguageCode(currentLanguage),
            filename: `voice-${Date.now()}.${extension}`
          });
          const speechText = voiceResponse.transcription?.text?.trim();

          if (!speechText) {
            toast.error("Voice query did not produce text.", {
              id: "voice-upload",
              duration: 4000,
              icon: "X"
            });
            return;
          }

          setMessage(message + (message ? " " : "") + speechText);
          setShowSpeechBadge(true);
          setTimeout(() => setShowSpeechBadge(false), 3000);
          toast.success(`Voice captured: "${speechText}"`, {
            id: "voice-upload",
            duration: 3000,
            icon: "Mic"
          });
        } catch (error) {
          console.error("Error uploading voice query:", error);
          toast.error("Voice transcription failed. Check the local STT service configuration.", {
            id: "voice-upload",
            duration: 5000,
            icon: "X"
          });
        } finally {
          setIsListening(false);
          setIsRecording(false);
          stopActiveStream();
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
      setIsListening(true);
      toast.success("Listening... Speak clearly", { duration: 2000, icon: "Mic" });
    } catch (error) {
      console.error("Error accessing microphone:", error);
      toast.error("Could not access microphone. Please check your microphone permissions.", {
        duration: 4000,
        icon: "X"
      });
      stopActiveStream();
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
    }
  };

  const handleMicrophoneClick = () => {
    if (isRecording) {
      stopRecording();
      return;
    }
    startRecording();
  };

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(false);
    const files = Array.from(event.dataTransfer.files);
    if (files.length > 0 && onFileUpload) {
      onFileUpload(files[0]);
    }
  };

  const handleInput = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    const textarea = event.target;
    const value = event.target.value;

    if (value.length > maxChars) {
      return;
    }

    setMessage(value);
    setShowPlaceholder(value.length === 0);
    textarea.style.height = "auto";
    const maxHeight = isExpanded ? 300 : 150;
    textarea.style.height = `${Math.min(textarea.scrollHeight, maxHeight)}px`;

    setIsTyping(true);
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }
    typingTimeoutRef.current = setTimeout(() => setIsTyping(false), 1000);
  };

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);

    if (textareaRef.current) {
      const textarea = textareaRef.current;

      if (!isExpanded) {
        gsap.to(textarea, {
          maxHeight: "300px",
          duration: 0.4,
          ease: "power2.out"
        });

        if (containerRef.current) {
          gsap.timeline()
            .to(containerRef.current, { scale: 1.01, duration: 0.15, ease: "power2.out" })
            .to(containerRef.current, { scale: 1, duration: 0.25, ease: "power2.out" });
        }
      } else {
        gsap.to(textarea, {
          maxHeight: "150px",
          duration: 0.3,
          ease: "power2.inOut"
        });
      }

      setTimeout(() => {
        textarea.style.height = "auto";
        const nextHeight = Math.min(textarea.scrollHeight, isExpanded ? 150 : 300);
        textarea.style.height = `${nextHeight}px`;
      }, 50);
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((event.ctrlKey || event.metaKey) && event.key === "e") {
      event.preventDefault();
      toggleExpanded();
      return;
    }

    if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === "Enter") {
      event.preventDefault();
      const textarea = event.currentTarget;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const newValue = message.substring(0, start) + "\n" + message.substring(end);
      setMessage(newValue);
      setTimeout(() => {
        textarea.selectionStart = textarea.selectionEnd = start + 1;
      }, 0);
      return;
    }

    onKeyDown(event);
  };

  const handleFocus = () => {
    setShowPlaceholder(false);
    setShowStats(true);
    if (containerRef.current) {
      gsap.to(containerRef.current, {
        boxShadow: "0 0 8px rgba(139, 92, 246, 0.1), 0 0 16px rgba(124, 58, 237, 0.05)",
        scale: 1.02,
        duration: 0.3,
        ease: "power2.out"
      });
    }
  };

  const handleBlur = () => {
    if (message.length === 0) {
      setShowPlaceholder(true);
    }
    setShowStats(false);
    if (containerRef.current) {
      gsap.to(containerRef.current, {
        boxShadow: "none",
        scale: 1,
        duration: 0.3,
        ease: "power2.out"
      });
    }
  };

  return (
    <div className="w-full flex flex-col relative">
      {attachments.length > 0 && (
        <div className="mb-3 flex flex-wrap gap-2">
          {attachments.map((attachment) => (
            <div
              key={attachment.id}
              className="relative bg-gray-800/40 backdrop-blur-sm border border-purple-400/20 rounded-lg p-2 flex items-center space-x-2 max-w-xs"
            >
              <div className="flex-shrink-0">
                {attachment.type === "image" ? (
                  attachment.preview ? (
                    <img src={attachment.preview} alt={attachment.file.name} className="w-8 h-8 object-cover rounded" />
                  ) : (
                    <FontAwesomeIcon icon={faFile} className="text-blue-400 w-8 h-8" />
                  )
                ) : attachment.type === "pdf" ? (
                  <FontAwesomeIcon icon={faFilePdf} className="text-red-400 w-8 h-8" />
                ) : (
                  <FontAwesomeIcon icon={faFile} className="text-gray-400 w-8 h-8" />
                )}
              </div>

              <div className="flex-1 min-w-0">
                <p className="text-white text-sm font-medium truncate">{attachment.file.name}</p>
                <p className="text-gray-400 text-xs">{(attachment.file.size / 1024 / 1024).toFixed(1)} MB</p>
              </div>

              {onRemoveAttachment && (
                <button
                  onClick={() => onRemoveAttachment(attachment.id)}
                  className="flex-shrink-0 text-gray-400 hover:text-red-400 transition-colors"
                  title="Remove file"
                >
                  <FontAwesomeIcon icon={faTimes} className="w-4 h-4" />
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="flex items-center w-full">
        <div
          ref={containerRef}
          className={`enhanced-chat-input flex items-center w-full transition-all duration-300 rounded-2xl sm:rounded-3xl ${isTyping ? "typing-animation" : ""} ${isDragOver ? "drag-over" : ""}`}
          style={{
            background: "transparent",
            border: "2px solid transparent",
            backgroundImage: charCount > maxChars * 0.9
              ? "linear-gradient(transparent, transparent), linear-gradient(135deg, #fbbf24, #f59e0b, #d97706)"
              : isDragOver
              ? "linear-gradient(rgba(0,0,0,0.15), rgba(0,0,0,0.15)), linear-gradient(135deg, rgba(168, 85, 247, 0.3), rgba(124, 58, 237, 0.2), rgba(139, 92, 246, 0.25))"
              : "linear-gradient(rgba(0,0,0,0.1), rgba(0,0,0,0.1)), linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(124, 58, 237, 0.15), rgba(168, 85, 247, 0.1))",
            backgroundOrigin: "border-box",
            backgroundClip: "content-box, border-box"
          }}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <div className="flex items-center px-2 sm:px-3 py-2 sm:py-3">
            <FontAwesomeIcon
              icon={faPaperclip}
              className="mx-1 sm:mx-2 cursor-pointer text-white/80 hover:text-white transition-colors"
              style={{ fontSize: window.innerWidth < 640 ? "14px" : "16px" }}
              title="Attach file"
              onClick={handleFileClick}
            />
          </div>

          <div className="flex-1 relative">
            {showSpeechBadge && (
              <div className="absolute right-3 top-2 z-10 bg-green-500/90 text-white text-xs px-2 py-1 rounded-full flex items-center gap-1 animate-fade-in">
                <span className="w-1.5 h-1.5 bg-white rounded-full animate-pulse"></span>
                <span>Speech to text</span>
              </div>
            )}

            {showPlaceholder && (
              <span
                ref={placeholderRef}
                className="absolute left-3 top-3 text-white/60 pointer-events-none select-none"
                style={{ fontSize: "inherit", lineHeight: "inherit" }}
              >
                {currentText}
                <span className="cursor-blink">|</span>
              </span>
            )}

            <textarea
              ref={textareaRef}
              className={`w-full p-2 sm:p-3 bg-transparent text-white focus:outline-none resize-none transition-all duration-300 text-sm sm:text-base mobile-scroll ${showPlaceholder ? "text-transparent" : "text-white"}`}
              value={message}
              onChange={handleInput}
              onKeyDown={handleKeyDown}
              onFocus={handleFocus}
              onBlur={handleBlur}
              rows={1}
              style={{
                maxHeight: isExpanded ? (window.innerWidth < 640 ? "200px" : "300px") : (window.innerWidth < 640 ? "120px" : "150px"),
                overflowY: "auto",
                scrollbarWidth: "thin",
                scrollbarColor: "rgba(139, 92, 246, 0.2) transparent",
                outline: "none",
                border: "none",
                boxShadow: "none",
                color: "#ffffff",
                fontWeight: "500"
              }}
            />
          </div>

          <div className="flex items-center px-2 sm:px-3 py-2 sm:py-3">
            <FontAwesomeIcon
              icon={faCopy}
              className={`mx-1 sm:mx-2 cursor-pointer transition-all duration-300 hidden xs:block ${message.trim() ? "text-white/80 hover:text-white" : "text-white/40 cursor-not-allowed"}`}
              style={{ fontSize: window.innerWidth < 640 ? "14px" : "16px" }}
              onClick={handleCopyText}
              title={message.trim() ? "Copy text" : "No text to copy"}
            />

            <select
              value={currentLanguage}
              onChange={(event) => setCurrentLanguage(event.target.value)}
              className="mx-1 sm:mx-2 bg-gray-700/50 text-white text-xs px-2 py-1 rounded border border-gray-600/50 focus:outline-none focus:ring-1 focus:ring-purple-400"
              title="Select speech input language"
            >
              {languageOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>

            {isListening && (
              <button
                onClick={handleMicrophoneClick}
                className="mx-1 sm:mx-2 cursor-pointer text-red-400 hover:text-red-300 transition-all duration-300 animate-pulse"
                title="Stop listening"
              >
                <FontAwesomeIcon icon={faTimes} style={{ fontSize: window.innerWidth < 640 ? "14px" : "16px" }} />
              </button>
            )}

            <FontAwesomeIcon
              icon={faMicrophone}
              className={`mx-1 sm:mx-2 cursor-pointer transition-all duration-300 ${isListening ? "text-green-400 hover:text-green-300 animate-pulse" : isRecording ? "text-red-400 hover:text-red-300 animate-pulse" : "text-white/80 hover:text-white"}`}
              style={{ fontSize: window.innerWidth < 640 ? "14px" : "16px" }}
              title={isRecording ? "Recording... Click to stop" : `Start voice query (${currentLanguage})`}
              onClick={handleMicrophoneClick}
            />

            <button
              onClick={toggleExpanded}
              className="mx-1 sm:mx-2 cursor-pointer text-white/80 hover:text-white hidden xs:block"
              title={isExpanded ? "Collapse" : "Expand"}
            >
              <FontAwesomeIcon
                icon={isExpanded ? faCompress : faExpand}
                className="transition-transform duration-300"
                style={{ fontSize: window.innerWidth < 640 ? "14px" : "16px" }}
              />
            </button>
          </div>
        </div>

        <BubblyButton
          onClick={onSendMessage}
          variant="primary"
          className="ml-2 sm:ml-3 send-button flex items-center justify-center transition-all duration-300 touch-target"
          disabled={!message.trim() && attachments.length === 0}
          style={{
            width: window.innerWidth < 640 ? "44px" : "48px",
            height: window.innerWidth < 640 ? "44px" : "48px",
            borderRadius: "50%",
            background: (message.trim() || attachments.length > 0)
              ? "linear-gradient(135deg, #61ACEF, #9987ED, #B679E1, #9791DB, #74BDCC, #59D2BF)"
              : "linear-gradient(135deg, #4B5563, #6B7280)",
            boxShadow: (message.trim() || attachments.length > 0)
              ? "0 2px 8px rgba(139, 92, 246, 0.15), 0 0 12px rgba(124, 58, 237, 0.1)"
              : "0 1px 4px rgba(75, 85, 99, 0.2)",
            transform: (message.trim() || attachments.length > 0) ? "scale(1)" : "scale(0.95)"
          }}
        >
          <FontAwesomeIcon
            className={`transition-all duration-300 ${(message.trim() || attachments.length > 0) ? "text-white text-base sm:text-lg" : "text-gray-400 text-sm sm:text-base"}`}
            icon={faArrowUp}
          />
        </BubblyButton>
      </div>

      <div className="absolute -top-6 sm:-top-8 left-2 sm:left-4 right-2 sm:right-4 flex justify-between items-center">
        {isListening && (
          <div className="flex items-center gap-2 text-green-400 animate-pulse">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-ping"></div>
            <span className="text-xs font-medium">Listening...</span>
          </div>
        )}

        {isTyping && !isListening && <div className="text-xs text-white/70 animate-pulse">Typing...</div>}

        {showStats && (isExpanded || charCount > 100) && (
          <div className="text-xs text-white/70 flex items-center gap-2 sm:gap-3 ml-auto">
            <span className={charCount > maxChars * 0.8 ? "text-yellow-400" : ""}>{charCount}/{maxChars}</span>
            <span className="hidden xs:inline">{wordCount} words</span>
            <span className="text-white/50 hidden lg:inline" title="Keyboard shortcuts">
              Ctrl+E: Expand
            </span>
          </div>
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.doc,.docx,.txt,image/*"
        onChange={handleFileChange}
        style={{ display: "none" }}
      />
    </div>
  );
};

export default EnhancedChatInput;
