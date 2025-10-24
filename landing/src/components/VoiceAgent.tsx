"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { X, Mic, MicOff, Phone } from "lucide-react";
import { useConversation } from "@elevenlabs/react";

interface VoiceAgentProps {
  isOpen: boolean;
  onClose: () => void;
}

export function VoiceAgent({ isOpen, onClose }: VoiceAgentProps) {
  const [isMuted, setIsMuted] = useState(false);
  const [agentState, setAgentState] = useState<string>("disconnected");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);

  const agentId = process.env.NEXT_PUBLIC_AGENT_ID || "";

  const conversation = useConversation({
    onConnect: () => {
      console.log("✅ Conectado al agente");
      setAgentState("connected");
      setIsLoading(false);
      setError(null);
    },
    onDisconnect: () => {
      console.log("❌ Desconectado del agente");
      setAgentState("disconnected");
      setIsLoading(false);
    },
    onMessage: (message) => {
      console.log("📨 Mensaje:", message);
    },
    onError: (error) => {
      console.error("❌ Error:", error);
      setAgentState("disconnected");
      setIsLoading(false);
      const errorObj =
        error instanceof Error
          ? error
          : new Error(typeof error === "string" ? error : JSON.stringify(error));
      setError(errorObj.message || "Error al conectar con el agente");
    },
  });

  const getMicStream = useCallback(async () => {
    if (mediaStreamRef.current) return mediaStreamRef.current;

    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      }
    });
    mediaStreamRef.current = stream;

    return stream;
  }, []);

  const handleConnect = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      if (!agentId) {
        throw new Error("Agent ID no configurado");
      }

      // Get microphone permission
      await getMicStream();

      // Start conversation with ElevenLabs
      await conversation.startSession({
        agentId,
        connectionType: "webrtc",
        onStatusChange: (status) => {
          console.log("🔄 Estado:", status.status);
          setAgentState(status.status);
        },
      });
    } catch (err: any) {
      console.error("Error connecting:", err);
      setError(err.message || "Error al conectar con el agente");
      setIsLoading(false);

      // Cleanup on error
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((track) => track.stop());
        mediaStreamRef.current = null;
      }
    }
  }, [conversation, getMicStream, agentId]);

  const handleDisconnect = useCallback(() => {
    conversation.endSession();
    setAgentState("disconnected");
    setIsLoading(false);
    setError(null);

    // Stop microphone
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }

    onClose();
  }, [conversation, onClose]);

  const toggleMute = useCallback(() => {
    setIsMuted((prev) => !prev);
    if (mediaStreamRef.current) {
      const audioTracks = mediaStreamRef.current.getAudioTracks();
      audioTracks.forEach((track) => {
        track.enabled = isMuted; // Toggle
      });
    }
  }, [isMuted]);

  useEffect(() => {
    return () => {
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  if (!isOpen) return null;

  const isConnected = agentState === "connected";
  const isConnecting = agentState === "connecting" || isLoading;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="relative w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">Asistente Virtual</h2>
          <button
            onClick={handleDisconnect}
            className="rounded-full p-2 hover:bg-gray-100 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Status Indicator */}
        <div className="mb-6 flex items-center justify-center">
          <div
            className={`relative h-32 w-32 rounded-full ${
              isConnected
                ? "bg-gradient-to-br from-primary to-secondary animate-pulse"
                : isConnecting
                ? "bg-gradient-to-br from-yellow-400 to-orange-500 animate-pulse"
                : "bg-gray-200"
            } flex items-center justify-center`}
          >
            {isConnecting ? (
              <div className="h-16 w-16 border-4 border-white border-t-transparent rounded-full animate-spin" />
            ) : isConnected ? (
              <Mic className="h-16 w-16 text-white" />
            ) : (
              <MicOff className="h-16 w-16 text-gray-400" />
            )}
          </div>
        </div>

        {/* Status Text */}
        <div className="mb-6 text-center">
          <p className="text-sm text-gray-700">
            {isConnecting
              ? "Conectando con el asistente..."
              : isConnected
              ? "Asistente: Buenos días, ¿en qué le puedo ayudar?"
              : "Presiona Hablar para iniciar"}
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 rounded-lg bg-red-50 border border-red-200 p-3">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {/* Controls */}
        <div className="flex gap-4">
          {!isConnected ? (
            <button
              onClick={handleConnect}
              disabled={isConnecting}
              className="flex-1 flex items-center justify-center gap-2 rounded-lg bg-primary px-6 py-3 font-semibold text-white hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isConnecting ? (
                <>
                  <div className="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Conectando...
                </>
              ) : (
                <>
                  <Mic className="h-5 w-5" />
                  Hablar
                </>
              )}
            </button>
          ) : (
            <>
              <button
                onClick={toggleMute}
                className={`flex-1 flex items-center justify-center gap-2 rounded-lg px-6 py-3 font-semibold transition-colors ${
                  isMuted
                    ? "bg-yellow-500 hover:bg-yellow-600 text-white"
                    : "bg-gray-200 hover:bg-gray-300 text-gray-700"
                }`}
              >
                {isMuted ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
                {isMuted ? "Silenciado" : "Hablar"}
              </button>
              <button
                onClick={handleDisconnect}
                className="flex-1 flex items-center justify-center gap-2 rounded-lg bg-red-500 px-6 py-3 font-semibold text-white hover:bg-red-600 transition-colors"
              >
                <Phone className="h-5 w-5 rotate-135" />
                Terminar
              </button>
            </>
          )}
        </div>

        {/* Info */}
        <div className="mt-4 space-y-1">
          <p className="text-center text-xs text-gray-500">
            Tu privacidad es importante. Las conversaciones no se graban.
          </p>
          {isConnected && (
            <p className="text-center text-xs text-green-600">
              ✓ Conectado • Micrófono activo
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
