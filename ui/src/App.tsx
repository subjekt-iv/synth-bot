import { BrowserRouter as Router, Routes, Route, Link, useLocation, useNavigate, useParams } from "react-router-dom";
import { QueryClient, QueryClientProvider, useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { MessageSquare, FileText, Plus, Trash2 } from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import { ChatPage } from "@/pages/ChatPage";
import { DocumentsPage } from "@/pages/DocumentsPage";
import { conversationsApi } from "@/api/chat";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuAction,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarRail,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      retry: 1,
    },
  },
});

function ConversationList() {
  const { conversationId } = useParams();
  const navigate = useNavigate();
  const qc = useQueryClient();

  const { data } = useQuery({
    queryKey: ["conversations"],
    queryFn: () => conversationsApi.list(),
  });

  const deleteMutation = useMutation({
    mutationFn: conversationsApi.delete,
    onSuccess: (_, deletedId) => {
      qc.invalidateQueries({ queryKey: ["conversations"] });
      if (conversationId === deletedId) {
        navigate("/");
      }
    },
  });

  const conversations = data?.conversations ?? [];
  if (conversations.length === 0) return null;

  return (
    <SidebarGroup>
      <SidebarGroupLabel>Recent Chats</SidebarGroupLabel>
      <SidebarGroupContent>
        <SidebarMenu>
          {conversations.map((conv) => (
            <SidebarMenuItem key={conv.id}>
              <SidebarMenuButton
                asChild
                isActive={conversationId === conv.id}
                tooltip={conv.title || "Untitled"}
              >
                <Link to={`/chat/${conv.id}`}>
                  <MessageSquare className="shrink-0" />
                  <span className="truncate">{conv.title || "Untitled"}</span>
                </Link>
              </SidebarMenuButton>
              <SidebarMenuAction
                showOnHover
                onClick={(e) => {
                  e.preventDefault();
                  deleteMutation.mutate(conv.id);
                }}
              >
                <Trash2 className="h-3.5 w-3.5" />
              </SidebarMenuAction>
            </SidebarMenuItem>
          ))}
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  );
}

function AppSidebar() {
  const location = useLocation();

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="flex items-center justify-center py-4">
        <Link to="/">
          <img
            src="/logo.png"
            alt="Synth Bot"
            className="size-12 rounded-lg object-cover"
          />
        </Link>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton
                  asChild
                  isActive={location.pathname === "/"}
                  tooltip="New Chat"
                >
                  <Link to="/">
                    <Plus />
                    <span>New Chat</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton
                  asChild
                  isActive={location.pathname === "/documents"}
                  tooltip="Manuals"
                >
                  <Link to="/documents">
                    <FileText />
                    <span>Manuals</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
        <ConversationList />
      </SidebarContent>
      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <ThemeToggle />
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}

function AppLayout() {
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <header className="flex h-12 shrink-0 items-center gap-2 border-b px-4 md:hidden">
          <SidebarTrigger />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <img src="/logo.png" alt="Synth Bot" className="size-6 rounded" />
          <span className="font-semibold">Synth Bot</span>
        </header>
        <div className="flex flex-1 flex-col overflow-hidden">
          <Routes>
            <Route path="/" element={<ChatPage />} />
            <Route path="/chat/:conversationId" element={<ChatPage />} />
            <Route path="/documents" element={<DocumentsPage />} />
          </Routes>
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <AppLayout />
      </Router>
    </QueryClientProvider>
  );
}

export default App;
