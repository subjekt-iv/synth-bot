import { useState, useEffect, useCallback, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Send, Copy, Check, Clock, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Message,
  MessageAvatar,
  MessageContent,
  MessageActions,
  MessageAction,
} from "@/components/ui/message";
import {
  PromptInput,
  PromptInputTextarea,
  PromptInputActions,
  PromptInputAction,
} from "@/components/ui/prompt-input";
import { PromptSuggestion } from "@/components/ui/prompt-suggestion";
import { Loader } from "@/components/ui/loader";
import { chatApi, conversationsApi, type Citation } from "@/api/chat";

interface LocalChatItem {
  id: string;
  user_query: string;
  ai_response: string;
  response_time?: number;
  citations?: Citation[];
}

const STARTER_PROMPTS = [
  "How do I set up MIDI on my synth?",
  "Explain the signal flow of a subtractive synthesizer",
  "What are the different filter types and how do they sound?",
  "How do I create a bass patch from an init preset?",
];

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [text]);

  return (
    <MessageAction tooltip={copied ? "Copied!" : "Copy"}>
      <Button variant="ghost" size="icon" className="h-6 w-6" onClick={handleCopy}>
        {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
      </Button>
    </MessageAction>
  );
}

function CitationList({ citations }: { citations: Citation[] }) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  return (
    <div className="mt-2 space-y-2">
      <p className="flex items-center gap-1 text-xs font-medium text-muted-foreground">
        <BookOpen className="h-3 w-3" />
        Sources
      </p>
      <div className="flex flex-wrap gap-1.5">
        {citations.map((cite) => (
          <button
            key={cite.chunk_id}
            onClick={() =>
              setExpandedId(expandedId === cite.chunk_id ? null : cite.chunk_id)
            }
            className={`inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs transition-colors ${
              expandedId === cite.chunk_id
                ? "bg-foreground/10 text-foreground"
                : "bg-muted text-muted-foreground hover:bg-foreground/5"
            }`}
          >
            p.{cite.page_number}
            {cite.relevance_score != null && (
              <span className="opacity-60">
                {Math.round(cite.relevance_score * 100)}%
              </span>
            )}
          </button>
        ))}
      </div>
      {expandedId && (
        <div className="rounded-md border bg-muted/50 p-3 text-xs text-muted-foreground leading-relaxed">
          {citations.find((c) => c.chunk_id === expandedId)?.content}
        </div>
      )}
    </div>
  );
}

export function ChatPage() {
  const { conversationId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [message, setMessage] = useState("");
  const [localChats, setLocalChats] = useState<LocalChatItem[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(
    conversationId ?? null
  );
  const bottomRef = useRef<HTMLDivElement>(null);

  // Load conversation history when navigating to an existing conversation
  const { data: conversationData, error: conversationError } = useQuery({
    queryKey: ["conversation", conversationId],
    queryFn: () => conversationsApi.get(conversationId!),
    enabled: !!conversationId,
    retry: false,
  });

  // Redirect to new chat if conversation not found
  useEffect(() => {
    if (conversationError) {
      navigate("/", { replace: true });
    }
  }, [conversationError, navigate]);

  // Sync conversation data into local state
  useEffect(() => {
    if (conversationData?.chats) {
      setLocalChats(
        conversationData.chats.map((c) => ({
          id: c.id,
          user_query: c.user_query,
          ai_response: c.ai_response,
          response_time: c.response_time,
          citations: c.citations,
        }))
      );
      setActiveConversationId(conversationData.id);
    }
  }, [conversationData]);

  // Reset when navigating to new chat (/)
  useEffect(() => {
    if (!conversationId) {
      setLocalChats([]);
      setActiveConversationId(null);
    }
  }, [conversationId]);

  const sendMessageMutation = useMutation({
    mutationFn: chatApi.sendMessage,
    onSuccess: (data, variables) => {
      setLocalChats((prev) => [
        ...prev,
        {
          id: `${Date.now()}-user`,
          user_query: variables.query,
          ai_response: "",
        },
        {
          id: `${Date.now()}-ai`,
          user_query: "",
          ai_response: data.response,
          response_time: data.response_time,
          citations: data.citations,
        },
      ]);

      // If this created a new conversation, navigate to it
      if (data.conversation_id && !activeConversationId) {
        setActiveConversationId(data.conversation_id);
        navigate(`/chat/${data.conversation_id}`, { replace: true });
      }

      // Refresh sidebar conversation list
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
    },
  });

  const handleSubmit = useCallback(() => {
    if (!message.trim()) return;
    const query = message.trim();
    setMessage("");
    sendMessageMutation.mutate({
      query,
      conversation_id: activeConversationId || undefined,
    });
  }, [message, sendMessageMutation, activeConversationId]);

  const handleSuggestionClick = useCallback(
    (suggestion: string) => {
      sendMessageMutation.mutate({
        query: suggestion,
        conversation_id: activeConversationId || undefined,
      });
    },
    [sendMessageMutation, activeConversationId]
  );

  const isLoading = sendMessageMutation.isPending;

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [localChats, isLoading]);

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 min-h-0 overflow-y-auto">
        <div className="flex flex-col gap-4 p-4 pb-0 max-w-3xl mx-auto w-full">
          {localChats.length === 0 && !isLoading && (
            <div className="flex flex-1 flex-col items-center justify-center gap-6 py-16">
              <img src="/logo.png" alt="Synth Bot" className="h-28 w-28 rounded-full object-cover" />
              <div className="text-center">
                <h2 className="text-xl font-semibold">Welcome to Synth Bot</h2>
                <p className="mt-1 text-sm text-muted-foreground">
                  Ask anything about your synthesizers and manuals
                </p>
              </div>
              <div className="flex flex-wrap justify-center gap-2">
                {STARTER_PROMPTS.map((prompt) => (
                  <PromptSuggestion
                    key={prompt}
                    onClick={() => handleSuggestionClick(prompt)}
                  >
                    {prompt}
                  </PromptSuggestion>
                ))}
              </div>
            </div>
          )}

          {localChats.map((chat, idx) => (
            <div key={chat.id + idx} className="space-y-4">
              {chat.user_query && (
                <Message className="justify-end">
                  <MessageContent className="bg-primary text-primary-foreground max-w-[80%]">
                    {chat.user_query}
                  </MessageContent>
                  <MessageAvatar src="" alt="You" fallback="Y" className="bg-foreground/10 text-foreground" />
                </Message>
              )}
              {chat.ai_response && (
                <div className="space-y-1">
                  <Message>
                    <img src="/logo.png" alt="Synth Bot" className="h-8 w-8 shrink-0 rounded-full object-cover" />
                    <div className="flex flex-col gap-1 max-w-[80%]">
                      <MessageContent
                        markdown
                        className="prose dark:prose-invert bg-secondary"
                      >
                        {chat.ai_response}
                      </MessageContent>
                      <div className="flex items-center gap-2">
                        <MessageActions>
                          <CopyButton text={chat.ai_response} />
                        </MessageActions>
                        {chat.response_time && (
                          <span className="flex items-center gap-1 text-xs text-muted-foreground">
                            <Clock className="h-3 w-3" />
                            {chat.response_time.toFixed(2)}s
                          </span>
                        )}
                      </div>
                      {chat.citations && chat.citations.length > 0 && (
                        <CitationList citations={chat.citations} />
                      )}
                    </div>
                  </Message>
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <Message>
              <img src="/logo.png" alt="Synth Bot" className="h-8 w-8 shrink-0 rounded-full object-cover" />
              <div className="rounded-lg bg-secondary p-3">
                <Loader variant="typing" size="sm" />
              </div>
            </Message>
          )}

          <div ref={bottomRef} />
        </div>
      </div>

      <div className="border-t bg-background p-4">
        <div className="mx-auto max-w-3xl">
          <PromptInput
            value={message}
            onValueChange={setMessage}
            isLoading={isLoading}
            onSubmit={handleSubmit}
            disabled={isLoading}
          >
            <PromptInputTextarea
              placeholder="Type your message..."
              autoFocus
            />
            <PromptInputActions className="justify-end px-2 pb-2">
              <PromptInputAction tooltip="Send message">
                <Button
                  variant="default"
                  size="icon"
                  className="h-8 w-8 rounded-full"
                  disabled={isLoading || !message.trim()}
                  onClick={handleSubmit}
                >
                  <Send className="h-4 w-4" />
                </Button>
              </PromptInputAction>
            </PromptInputActions>
          </PromptInput>
        </div>
      </div>
    </div>
  );
}
